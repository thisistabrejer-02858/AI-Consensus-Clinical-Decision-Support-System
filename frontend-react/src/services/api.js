export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/+$/, '')

const REQUEST_TIMEOUT_MS = 300_000
const USE_LOCAL_DEV_PROXY =
  import.meta.env.DEV && API_BASE_URL === 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  const controller = new AbortController()
  const timeout = window.setTimeout(
    () => controller.abort(),
    REQUEST_TIMEOUT_MS,
  )

  try {
    const url = USE_LOCAL_DEV_PROXY
      ? `/api${path}`
      : `${API_BASE_URL}${path}`
    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: 'application/json',
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
      signal: controller.signal,
    })

    const body = await response.text()
    let data
    if (body) {
      try {
        data = JSON.parse(body)
      } catch {
        if (response.ok) {
          throw new Error(`The backend returned invalid JSON for ${path}.`)
        }
      }
    }

    if (!response.ok) {
      const detail = data?.detail
      const message =
        typeof detail === 'string'
          ? detail
          : Array.isArray(detail)
            ? detail.map((item) => item.msg || JSON.stringify(item)).join('; ')
            : `The backend returned HTTP ${response.status}.`
      throw new Error(message)
    }

    if (data === undefined) {
      throw new Error(`The backend returned an empty response for ${path}.`)
    }

    return data
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('The request timed out. Check the backend and try again.')
    }
    if (error instanceof TypeError) {
      throw new Error(
        'Could not reach the backend. Confirm it is running and that its API URL is correct.',
      )
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
  }
}

export function getHealth() {
  return request('/health/')
}

export function createDiagnosis(patientCase) {
  return request('/diagnosis/', {
    method: 'POST',
    body: JSON.stringify(patientCase),
  })
}

export function evaluateCases(cases) {
  return request('/evaluation/', {
    method: 'POST',
    body: JSON.stringify({ cases }),
  })
}

export function isConsensusResult(value) {
  return (
    value !== null &&
    typeof value === 'object' &&
    (value.primary_diagnosis === null ||
      typeof value.primary_diagnosis === 'string') &&
    typeof value.agreement_score === 'number' &&
    typeof value.consensus_score === 'number' &&
    Array.isArray(value.candidates) &&
    Array.isArray(value.model_runs) &&
    value.model_runs.every(
      (run) =>
        typeof run.model_name === 'string' &&
        typeof run.provider === 'string' &&
        ['success', 'failed', 'timeout'].includes(run.status) &&
        (run.diagnosis === null || typeof run.diagnosis === 'string') &&
        (run.latency_ms === null || typeof run.latency_ms === 'number') &&
        (run.error_message === null || typeof run.error_message === 'string'),
    ) &&
    value.candidates.every(
      (candidate) =>
        typeof candidate.diagnosis === 'string' &&
        Array.isArray(candidate.supporting_models) &&
        typeof candidate.support_count === 'number' &&
        typeof candidate.weighted_support === 'number',
    )
  )
}
