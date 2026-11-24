import { useState } from 'react'
import { ArrowRight, RotateCcw, Send } from 'lucide-react'
import { useNavigate, useOutletContext } from 'react-router-dom'
import { Button, Card, CardHeading, ErrorState, PageHeader } from '../components/UI'
import { createDiagnosis, isConsensusResult } from '../services/api'

const emptyCase = {
  age: '',
  gender: '',
  symptoms: [],
  symptom_duration: '',
  medical_history: [],
  current_medications: [],
  allergies: [],
  test_results: [],
}

function ChipField({ label, hint, values, onChange, placeholder }) {
  const [draft, setDraft] = useState('')
  const inputId = `chip-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`
  const addDraft = () => {
    const additions = draft
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean)
    if (additions.length) {
      onChange([...new Set([...values, ...additions])])
      setDraft('')
    }
  }

  return (
    <div className="field-group">
      <label htmlFor={inputId}>{label}</label>
      {hint && <span className="field-hint">{hint}</span>}
      <div className="chip-input-wrap">
        {values.map((value, index) => (
          <span className="input-chip" key={`${value}-${index}`}>
            {value}
            <button
              type="button"
              aria-label={`Remove ${value}`}
              onClick={() => onChange(values.filter((_, i) => i !== index))}
            >
              ×
            </button>
          </span>
        ))}
        <input
          id={inputId}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ',') {
              event.preventDefault()
              addDraft()
            }
          }}
          onBlur={addDraft}
          placeholder={placeholder}
          aria-label={label}
        />
      </div>
      <span className="field-help">Press Enter or use commas to add items.</span>
    </div>
  )
}

export default function NewCase() {
  const navigate = useNavigate()
  const { addAnalysis, setActiveResult } = useOutletContext()
  const [form, setForm] = useState(emptyCase)
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }))

  const reset = () => {
    setForm(emptyCase)
    setErrors({})
    setSubmitError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const age = Number(form.age)
    const nextErrors = {}
    if (form.age === '' || !Number.isInteger(age) || age < 0 || age > 120) {
      nextErrors.age = 'Enter a whole number between 0 and 120.'
    }
    if (!form.gender.trim()) nextErrors.gender = 'Enter a gender description.'
    if (!form.symptoms.map((value) => value.trim()).filter(Boolean).length) {
      nextErrors.symptoms = 'Add at least one symptom.'
    }
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length) return

    const patientCase = {
      case_id: null,
      age,
      gender: form.gender.trim(),
      symptoms: form.symptoms.map((value) => value.trim()).filter(Boolean),
      symptom_duration: form.symptom_duration.trim() || null,
      medical_history: form.medical_history.map((value) => value.trim()).filter(Boolean),
      current_medications: form.current_medications.map((value) => value.trim()).filter(Boolean),
      allergies: form.allergies.map((value) => value.trim()).filter(Boolean),
      test_results: form.test_results.map((value) => value.trim()).filter(Boolean),
    }

    setSubmitting(true)
    setSubmitError('')
    try {
      const result = await createDiagnosis(patientCase)
      if (!isConsensusResult(result)) {
        throw new Error('The response did not match the expected consensus result format.')
      }
      setActiveResult(result)
      const saved = addAnalysis(result)
      navigate(`/results/${saved.id}`)
    } catch (error) {
      setSubmitError(error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="CASE ANALYSIS"
        title="New case analysis"
        description="Generate a multi-model AI consensus summary to support clinical review."
      />
      {submitError && (
        <ErrorState
          title="Analysis could not be completed"
          message={submitError}
        />
      )}

      <form className="case-form" onSubmit={handleSubmit} noValidate>
        <Card className="form-section">
          <CardHeading title="Basic information" description="Required fields are marked with an asterisk." />
          <div className="form-grid form-grid-two">
            <div className="field-group">
              <label htmlFor="age">Age <span className="required">*</span></label>
              <input
                id="age"
                type="number"
                min="0"
                max="120"
                step="1"
                inputMode="numeric"
                value={form.age}
                onChange={(event) => update('age', event.target.value)}
                aria-invalid={Boolean(errors.age)}
                aria-describedby={errors.age ? 'age-error' : 'age-help'}
              />
              {errors.age ? <span className="field-error" id="age-error">{errors.age}</span> : <span className="field-help" id="age-help">Whole number, 0 to 120.</span>}
            </div>
            <div className="field-group">
              <label htmlFor="gender">Gender <span className="required">*</span></label>
              <select
                id="gender"
                value={form.gender}
                onChange={(event) => update('gender', event.target.value)}
                aria-invalid={Boolean(errors.gender)}
                aria-describedby={errors.gender ? 'gender-error' : 'gender-help'}
              >
                <option value="">Select gender</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Non-binary">Non-binary</option>
                <option value="Another gender identity">Another gender identity</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
              {errors.gender ? (
                <span className="field-error" id="gender-error">{errors.gender}</span>
              ) : (
                <span className="field-help" id="gender-help">Choose the description provided for this case.</span>
              )}
            </div>
          </div>
        </Card>

        <Card className="form-section">
          <CardHeading title="Symptoms" description="Add one or more concise symptom descriptions." />
          <ChipField
            label="Symptoms"
            hint="At least one is required."
            values={form.symptoms}
            onChange={(value) => update('symptoms', value)}
            placeholder="Type a symptom and press Enter"
          />
          {errors.symptoms && <span className="field-error" id="symptoms-error">{errors.symptoms}</span>}
          <div className="field-group duration-field">
            <label htmlFor="duration">Symptom duration</label>
            <input id="duration" value={form.symptom_duration} onChange={(event) => update('symptom_duration', event.target.value)} placeholder="e.g. approximately three days" />
          </div>
        </Card>

        <Card className="form-section">
          <CardHeading title="Medical background" description="All fields are optional; leave blank when not applicable." />
          <div className="form-grid">
            <ChipField label="Medical history" values={form.medical_history} onChange={(value) => update('medical_history', value)} placeholder="Add a history item" />
            <ChipField label="Current medications" values={form.current_medications} onChange={(value) => update('current_medications', value)} placeholder="Add a medication" />
            <ChipField label="Allergies" values={form.allergies} onChange={(value) => update('allergies', value)} placeholder="Add an allergy" />
          </div>
        </Card>

        <Card className="form-section">
          <CardHeading title="Investigation details" description="Add relevant test information when available." />
          <ChipField label="Test results" values={form.test_results} onChange={(value) => update('test_results', value)} placeholder="Add a test result" />
        </Card>

        <div className="form-footer">
          <Button type="button" variant="tertiary" onClick={reset} disabled={submitting}>
            <RotateCcw size={16} /> Reset form
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? <span className="button-spinner" /> : <Send size={16} />}
            {submitting ? 'Waiting for model responses…' : 'Run analysis'}
            {!submitting && <ArrowRight size={16} />}
          </Button>
        </div>
      </form>
    </>
  )
}
