import { useCallback, useState } from 'react'

const STORAGE_KEY = 'clinical-consensus.analysis-history.v1'

function readHistory() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    const items = raw ? JSON.parse(raw) : []
    if (
      !Array.isArray(items) ||
      items.some(
        (item) =>
          typeof item?.id !== 'string' ||
          typeof item?.createdAt !== 'string' ||
          !item?.result ||
          typeof item.result !== 'object',
      )
    ) {
      throw new Error('Saved history has an unexpected format.')
    }
    return { items, error: null }
  } catch (error) {
    return {
      items: [],
      error: `Browser history could not be loaded: ${error.message}`,
    }
  }
}

export default function useHistory() {
  const [stored, setStored] = useState(readHistory)

  const persist = useCallback((nextItems) => {
    setStored((current) => ({ ...current, items: nextItems }))
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextItems))
      setStored({ items: nextItems, error: null })
    } catch (error) {
      setStored({
        items: nextItems,
        error: `Browser history could not be saved: ${error.message}`,
      })
    }
  }, [])

  const addAnalysis = useCallback(
    (result) => {
      const item = {
        id:
          typeof crypto !== 'undefined' && crypto.randomUUID
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        createdAt: new Date().toISOString(),
        result,
      }
      persist([item, ...stored.items].slice(0, 50))
      return item
    },
    [persist, stored.items],
  )

  const deleteAnalysis = useCallback(
    (id) => persist(stored.items.filter((item) => item.id !== id)),
    [persist, stored.items],
  )

  const clearHistory = useCallback(() => persist([]), [persist])

  return {
    history: stored.items,
    historyError: stored.error,
    addAnalysis,
    deleteAnalysis,
    clearHistory,
  }
}
