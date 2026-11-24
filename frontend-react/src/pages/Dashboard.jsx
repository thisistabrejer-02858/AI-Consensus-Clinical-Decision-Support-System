import {
  ArrowUpRight,
  ClipboardPlus,
  Clock3,
  ShieldCheck,
} from 'lucide-react'
import { Link, useOutletContext } from 'react-router-dom'
import { ActionLink, Card, CardHeading, EmptyState, PageHeader } from '../components/UI'
import { formatDate } from '../utils/format'

export default function Dashboard() {
  const { history, historyError } = useOutletContext()
  const latest = history[0]
  const candidates = latest?.result?.candidates || []

  return (
    <>
      <PageHeader
        eyebrow="OVERVIEW"
        title="AI Consensus Clinical Decision Support System"
        description="Review a multi-model analysis, see where the models align, and identify areas that may need further attention."
        action={
          <ActionLink to="/new-case">
            <ClipboardPlus size={17} />
            New analysis
          </ActionLink>
        }
      />

      <div className="dashboard-hero">
        <div className="hero-copy">
          <span className="hero-kicker">
            <span className="hero-kicker-dot" />
            MULTI-MODEL AI CONSENSUS
          </span>
          <h2>Multiple model perspectives. One clearer view.</h2>
          <p>
            Review AI-generated candidate summaries and model agreement to
            support informed clinical review.
          </p>
          <ActionLink to="/new-case" variant="secondary">
            Start an analysis <ArrowUpRight size={16} />
          </ActionLink>
        </div>
        <div className="hero-aside">
          <div className="hero-orbit">
            <div className="orbit-center"><ShieldCheck size={26} /></div>
            <span className="orbit-node node-one" />
            <span className="orbit-node node-two" />
            <span className="orbit-node node-three" />
          </div>
          <span>Model agreement does not confirm a diagnosis.</span>
        </div>
      </div>

      <div className="overview-grid">
        <Card className="overview-stat">
          <div className="stat-label"><Clock3 size={16} /> Saved analyses</div>
          <div className="stat-value">{history.length}</div>
          <p>Stored in this browser only</p>
        </Card>
        <Card className="overview-stat overview-stat-note">
          <div className="stat-label"><ShieldCheck size={16} /> Your data</div>
          <div className="stat-note-title">This browser only</div>
          <p>No sign-in or database is used for saved analyses</p>
        </Card>
      </div>

      {historyError && (
        <div className="inline-notice warning-notice" role="status">
          {historyError}
        </div>
      )}

      <div className="content-grid dashboard-content-grid">
        <Card>
          <CardHeading
            title="Recent analyses"
            description="Your most recent browser-saved results."
            action={
              history.length > 0 && (
                <Link to="/history" className="text-link">View history</Link>
              )
            }
          />
          {latest ? (
            <div className="recent-analysis">
              <div className="recent-icon"><ClipboardPlus size={18} /></div>
              <div className="recent-copy">
                <strong>
                  {latest.result.primary_diagnosis ||
                    'No unique consensus reached'}
                </strong>
                <span>{formatDate(latest.createdAt)}</span>
              </div>
              <Link
                to={`/results/${latest.id}`}
                className="round-link"
                aria-label="Open latest analysis"
              >
                <ArrowUpRight size={17} />
              </Link>
              {candidates.length > 0 && (
                <div className="recent-tags">
                  {candidates.slice(0, 3).map((candidate) => (
                    <span key={candidate.diagnosis}>{candidate.diagnosis}</span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <EmptyState
              title="Your workspace is ready"
              message="Your results will appear here after you complete an analysis."
              action={
                <ActionLink to="/new-case" variant="secondary">
                  Create an analysis
                </ActionLink>
              }
            />
          )}
        </Card>

        <Card className="project-card">
          <CardHeading
            title="How it works"
            description="A simple guide to reviewing an analysis."
          />
          <div className="project-steps">
            <div><span>01</span><p>Enter case details for analysis.</p></div>
            <div><span>02</span><p>Review candidate summaries from multiple AI models.</p></div>
            <div><span>03</span><p>Consider disagreement with a qualified professional.</p></div>
          </div>
          <Link to="/about" className="text-link project-link">
            About this system <ArrowUpRight size={14} />
          </Link>
        </Card>
      </div>
    </>
  )
}
