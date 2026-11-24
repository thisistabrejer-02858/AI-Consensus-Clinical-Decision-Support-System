import { Link } from 'react-router-dom'
import { AlertCircle, ArrowRight, LoaderCircle } from 'lucide-react'

export function Button({
  children,
  className = '',
  variant = 'primary',
  ...props
}) {
  return (
    <button
      className={`button button-${variant} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  )
}

export function ActionLink({
  children,
  to,
  className = '',
  variant = 'primary',
}) {
  return (
    <Link className={`button button-${variant} ${className}`.trim()} to={to}>
      {children}
    </Link>
  )
}

export function PageHeader({ eyebrow, title, description, action }) {
  return (
    <div className="page-header">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {description && <p className="page-description">{description}</p>}
      </div>
      {action && <div className="page-header-action">{action}</div>}
    </div>
  )
}

export function Card({ children, className = '', ...props }) {
  return (
    <section className={`card ${className}`.trim()} {...props}>
      {children}
    </section>
  )
}

export function CardHeading({ title, description, action }) {
  return (
    <div className="card-heading">
      <div>
        <h2>{title}</h2>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  )
}

export function LoadingState({ label = 'Loading' }) {
  return (
    <div className="state-panel" role="status" aria-live="polite">
      <LoaderCircle className="spin state-icon" size={22} />
      <div>
        <strong>{label}</strong>
        <p>Please wait while the information is retrieved.</p>
      </div>
    </div>
  )
}

export function ErrorState({ title = 'Something went wrong', message, action }) {
  return (
    <div className="state-panel state-error" role="alert">
      <AlertCircle className="state-icon" size={22} />
      <div>
        <strong>{title}</strong>
        <p>{message}</p>
        {action && <div className="state-action">{action}</div>}
      </div>
    </div>
  )
}

export function EmptyState({ title, message, action }) {
  return (
    <div className="empty-state">
      <div className="empty-mark">
        <ArrowRight size={19} />
      </div>
      <h3>{title}</h3>
      <p>{message}</p>
      {action && <div className="empty-action">{action}</div>}
    </div>
  )
}

export function CertificationNotice() {
  return (
    <aside className="certification-disclaimer" aria-label="Certification status">
      <span className="safety-dot" aria-hidden="true" />
      <span>Not clinically certified</span>
    </aside>
  )
}

export function StatusPill({ status }) {
  const labels = {
    checking: 'Checking…',
    online: 'Available',
    offline: 'Unavailable',
  }
  return (
    <span className={`status-pill status-${status}`}>
      <span className="status-dot" />
      {labels[status] || labels.checking}
    </span>
  )
}
