import { ArrowUpRight, Clock3, Trash2 } from 'lucide-react'
import { Link, useOutletContext } from 'react-router-dom'
import {
  Button,
  Card,
  CardHeading,
  EmptyState,
  ErrorState,
  PageHeader,
} from '../components/UI'
import { formatDate } from '../utils/format'

export default function History() {
  const { history, historyError, deleteAnalysis, clearHistory } = useOutletContext()

  const removeOne = (id) => {
    if (window.confirm('Delete this saved analysis from this browser?')) {
      deleteAnalysis(id)
    }
  }

  const removeAll = () => {
    if (window.confirm('Clear all saved analyses from this browser? This cannot be undone.')) {
      clearHistory()
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="SAVED ON THIS DEVICE"
        title="Your analysis history"
        description="Saved results are available only in this browser on this device. There is no account, cloud sync, or patient database."
        action={
          history.length > 0 && (
            <Button type="button" variant="tertiary" onClick={removeAll}>
              <Trash2 size={16} /> Clear history
            </Button>
          )
        }
      />
      {historyError && <ErrorState title="Browser storage notice" message={historyError} />}
      <Card>
        <CardHeading
          title="Saved on this device"
          description={`${history.length} ${history.length === 1 ? 'analysis' : 'analyses'} in this browser.`}
        />
        {history.length ? (
          <div className="history-list">
            {history.map((item) => (
              <article className="history-row" key={item.id}>
                <div className="history-mark"><Clock3 size={17} /></div>
                <div className="history-copy">
                  <Link to={`/results/${item.id}`} className="history-title">
                    {item.result.primary_diagnosis || 'No unique consensus reached'}
                  </Link>
                  <span>{formatDate(item.createdAt)}</span>
                  <div className="history-meta">
                    {item.result.candidates?.length || 0} candidate diagnoses
                    {item.result.disagreement_detected && <span className="disagreement-label">Disagreement detected</span>}
                  </div>
                </div>
                <div className="history-actions">
                  <Link
                    to={`/results/${item.id}`}
                    className="round-link"
                    aria-label="Open saved results"
                  >
                    <ArrowUpRight size={16} />
                  </Link>
                  <Button
                    type="button"
                    variant="icon"
                    aria-label="Delete saved analysis"
                    onClick={() => removeOne(item.id)}
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No saved analyses yet"
            message="Your completed analyses will appear here. Nothing is saved to an account or database."
          />
        )}
      </Card>
      <div className="history-storage-note">
        <span className="status-dot" />
        This browser only · Up to 50 recent result summaries
      </div>
    </>
  )
}
