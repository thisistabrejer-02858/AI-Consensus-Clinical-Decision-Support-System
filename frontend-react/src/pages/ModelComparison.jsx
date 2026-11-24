import { Info, Scale } from 'lucide-react'
import { Link, useOutletContext, useParams } from 'react-router-dom'
import {
  Card,
  CardHeading,
  EmptyState,
  PageHeader,
} from '../components/UI'

export default function ModelComparison() {
  const { analysisId } = useParams()
  const { history, activeResult } = useOutletContext()
  const saved = analysisId
    ? history.find((item) => item.id === analysisId)
    : null
  const result = saved?.result || (!analysisId ? activeResult : null)
  const candidates = result?.candidates || []

  return (
    <>
      <PageHeader
        eyebrow="RESPONSE REVIEW"
        title="Multi-model comparison"
        description="Review which AI models supported each candidate in the analysis."
        action={result && <span className="count-badge"><Scale size={14} /> Result summary</span>}
      />
      <div className="notice-banner info-banner">
        <Info size={18} />
        <p>
          The current result shows shared candidates and which AI models supported them; it does not include a separate full response from each model.
        </p>
      </div>
      {!result ? (
        <Card>
          <EmptyState
            title="No result to compare"
            message="Complete an analysis or choose a saved result from history to review its candidate support."
            action={<Link className="button button-secondary" to="/history">Open analysis history</Link>}
          />
        </Card>
      ) : candidates.length ? (
        <Card>
          <CardHeading
            title="Candidate support"
            description="See which AI models supported each candidate in the result."
          />
          <div className="comparison-table-wrap">
            <table className="data-table comparison-table">
              <thead>
                <tr>
                  <th scope="col">Candidate diagnosis</th>
                  <th scope="col">Supporting models</th>
                  <th scope="col">Support count</th>
                  <th scope="col">Weighted support</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate, index) => (
                  <tr key={`${candidate.diagnosis}-${index}`}>
                    <td>
                      <strong>{candidate.diagnosis}</strong>
                      {candidate.diagnosis === result.primary_diagnosis && (
                        <span className="table-tag">Primary</span>
                      )}
                    </td>
                    <td>
                      {candidate.supporting_models.length
                        ? <span className="model-chip">{candidate.supporting_models.join(', ')}</span>
                        : <span className="muted-copy">Not provided</span>}
                    </td>
                    <td>{candidate.support_count}</td>
                    <td>{candidate.weighted_support.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card>
          <EmptyState title="No candidate support to compare" message="The selected result does not contain candidate diagnoses." />
        </Card>
      )}
      {result && (
        <div className="comparison-disclaimer">
          <Card>
            <div className="limitation-copy">
              <Info size={18} />
              <p>
                Individual model reasoning and confidence scores are not included in this result. The diagnosis, status, and latency for each provider are shown in the results summary.
              </p>
            </div>
          </Card>
        </div>
      )}
    </>
  )
}
