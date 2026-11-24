import {
  AlertTriangle,
  ArrowLeft,
  ClipboardList,
  Info,
  Microscope,
  ShieldCheck,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link, useOutletContext, useParams } from 'react-router-dom'
import {
  ActionLink,
  Card,
  CardHeading,
  EmptyState,
  PageHeader,
} from '../components/UI'
import { formatDate, formatPercent } from '../utils/format'

function ScoreCard({ label, score, detail }) {
  const percent = Math.max(0, Math.min(100, Math.round(score * 100)))
  return (
    <Card className="score-card">
      <div className="score-label">{label}</div>
      <div className="score-value">{formatPercent(score)}</div>
      <div className="score-meter" aria-label={`${label}: ${percent}%`}>
        <span style={{ width: `${percent}%` }} />
      </div>
      <p>{detail}</p>
    </Card>
  )
}

export default function Results() {
  const { analysisId } = useParams()
  const { history, activeResult } = useOutletContext()
  const saved = analysisId
    ? history.find((item) => item.id === analysisId)
    : null
  const result = saved?.result || (!analysisId ? activeResult : null)

  if (!result) {
    return (
      <>
        <PageHeader eyebrow="ANALYSIS" title="Diagnosis results" />
        <Card>
          <EmptyState
            title="No analysis to display"
            message="Complete an analysis or open a saved result from your browser history."
            action={<ActionLink to="/new-case">Start a new analysis</ActionLink>}
          />
        </Card>
      </>
    )
  }

  const candidates = Array.isArray(result.candidates) ? result.candidates : []
  const modelRuns = Array.isArray(result.model_runs) ? result.model_runs : []
  const chartData = candidates.map((candidate) => ({
    diagnosis: candidate.diagnosis,
    support: candidate.weighted_support,
  }))

  return (
    <>
      <PageHeader
        eyebrow={saved ? `SAVED ANALYSIS · ${formatDate(saved.createdAt)}` : 'ANALYSIS COMPLETE'}
        title="Diagnosis results"
        description="A structured summary of candidate support and areas of agreement or disagreement."
        action={
          <Link to="/new-case" className="button button-secondary">
            <ArrowLeft size={16} /> New case
          </Link>
        }
      />

      {result.disagreement_detected && (
        <div className="notice-banner disagreement-banner" role="status">
          <AlertTriangle size={19} />
          <div>
            <strong>Disagreement detected</strong>
            <p>{result.disagreement_summary || 'The response indicates disagreement across the candidate set.'}</p>
          </div>
        </div>
      )}

      <Card className={`diagnosis-hero ${result.primary_diagnosis ? '' : 'diagnosis-empty'}`}>
        <div className="diagnosis-icon"><ShieldCheck size={21} /></div>
        <div className="diagnosis-copy">
          <span className="eyebrow">PRIMARY DIAGNOSIS</span>
          {result.primary_diagnosis ? (
            <h2>{result.primary_diagnosis}</h2>
          ) : (
            <>
              <h2>No unique consensus</h2>
              <p>No primary diagnosis was returned by the backend.</p>
            </>
          )}
        </div>
        {!result.primary_diagnosis && (
          <p className="no-consensus-callout">
            The models did not agree on one result. Review the candidate summaries and discuss any concerns with a qualified professional.
          </p>
        )}
      </Card>

      <div className="score-grid">
        <ScoreCard
          label="Agreement score"
          score={result.agreement_score}
          detail="Shows how closely the model outputs align. It is not accuracy."
        />
        <ScoreCard
          label="Consensus score"
          score={result.consensus_score}
          detail="A model-consensus measure, not the probability of a diagnosis."
        />
        <Card className="score-explainer">
          <div className="explainer-icon"><Info size={17} /></div>
          <strong>How to read these scores</strong>
          <p>Agreement and consensus are not measures of diagnostic accuracy or probability that a diagnosis is correct.</p>
        </Card>
      </div>

      {result.explanation && (
        <Card className="explanation-card">
          <CardHeading title="Explanation" />
          <p className="prose-copy">{result.explanation}</p>
        </Card>
      )}

      <div className="content-grid results-grid">
        <Card>
          <CardHeading
            title="Candidate diagnoses"
            description="Weighted support is displayed as returned; it is not a probability."
            action={<span className="count-badge">{candidates.length} candidates</span>}
          />
          {candidates.length ? (
            <div className="candidate-list">
              {candidates.map((candidate, index) => (
                <div className="candidate-row" key={`${candidate.diagnosis}-${index}`}>
                  <span className="candidate-rank">{String(index + 1).padStart(2, '0')}</span>
                  <div className="candidate-main">
                    <strong>{candidate.diagnosis}</strong>
                    <span>
                      {candidate.supporting_models.length > 0
                        ? `Supported by ${candidate.supporting_models.join(', ')}`
                        : `${candidate.support_count} supporting model${candidate.support_count === 1 ? '' : 's'}`}
                    </span>
                  </div>
                  <span className="candidate-weight">{candidate.weighted_support.toFixed(2)}</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="No candidates returned" message="The API response did not include candidate diagnoses." />
          )}
        </Card>
        <Card>
          <CardHeading title="Weighted support" description="Candidate values from the API response." />
          {chartData.length ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={Math.max(180, chartData.length * 52)}>
                <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 12, left: 8, bottom: 4 }}>
                  <CartesianGrid stroke="#edf0ec" horizontal={false} />
                  <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#52645a', fontSize: 14 }} />
                  <YAxis type="category" dataKey="diagnosis" width={142} axisLine={false} tickLine={false} tick={{ fill: '#35483b', fontSize: 14 }} />
                  <Tooltip cursor={{ fill: '#f5f7f4' }} formatter={(value) => [Number(value).toFixed(2), 'Weighted support']} />
                  <Bar dataKey="support" fill="#668278" radius={[0, 5, 5, 0]} barSize={18} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState title="Chart unavailable" message="No candidate support values were returned." />
          )}
        </Card>
      </div>

      <div className="content-grid results-grid results-lower">
        <Card>
          <CardHeading title="Recommended tests" description="Recommendations included in the backend response." />
          {result.recommended_tests?.length ? (
            <ul className="recommendation-list">
              {result.recommended_tests.map((item, index) => (
                <li key={`${item}-${index}`}><Microscope size={16} />{item}</li>
              ))}
            </ul>
          ) : (
            <p className="muted-copy">No recommended tests were provided.</p>
          )}
        </Card>
        <Card>
          <CardHeading title="Model response details" description="Outcome from each configured provider." />
          {modelRuns.length ? (
            <ul className="model-run-list">
              {modelRuns.map((run) => (
                <li className="model-run-item" key={`${run.provider}-${run.model_name}`}>
                  <div className="model-run-main">
                    <strong>{run.model_name}</strong>
                    <span>{run.provider} · {run.diagnosis || (run.status === 'success' ? 'No usable diagnosis returned' : 'No diagnosis returned')}</span>
                    {run.error_message && <span className="model-run-error">{run.error_message}</span>}
                  </div>
                  <div className="model-run-meta">
                    <span className={`model-run-status ${run.status}`}>{run.status}</span>
                    {typeof run.latency_ms === 'number' && <span>{Math.round(run.latency_ms)} ms</span>}
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="limitation-copy">
              <ClipboardList size={18} />
              <p>Per-model details are not available for this saved result.</p>
            </div>
          )}
        </Card>
      </div>

      <div className="results-actions">
        <Link to={saved ? `/comparison/${saved.id}` : '/comparison'} className="text-link">
          Continue to model comparison <ArrowLeft size={15} className="flip-icon" />
        </Link>
      </div>
    </>
  )
}
