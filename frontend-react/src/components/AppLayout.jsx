import { useEffect, useState } from 'react'
import {
  Activity,
  ClipboardPlus,
  FlaskConical,
  History,
  Info,
  LayoutDashboard,
  Menu,
  Scale,
  X,
} from 'lucide-react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { getHealth } from '../services/api'
import { CertificationNotice, StatusPill } from './UI'

const navigation = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard, end: true },
  { label: 'New case analysis', to: '/new-case', icon: ClipboardPlus },
  { label: 'History · this browser', to: '/history', icon: History },
  { label: 'Model comparison', to: '/comparison', icon: Scale },
  { label: 'Evaluation & benchmarks', to: '/evaluation', icon: FlaskConical },
  { label: 'About', to: '/about', icon: Info },
]

const pageTitles = {
  '/': 'Dashboard',
  '/new-case': 'New case analysis',
  '/history': 'Your analysis history',
  '/comparison': 'Model comparison',
  '/evaluation': 'Evaluation & benchmarks',
  '/about': 'About',
}

export default function AppLayout({ appContext }) {
  const [health, setHealth] = useState('checking')
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()
  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        const response = await getHealth()
        if (active) {
          setHealth(response?.status === 'ok' ? 'online' : 'offline')
        }
      } catch {
        if (active) setHealth('offline')
      }
    }
    check()
    const interval = window.setInterval(check, 45_000)
    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [])

  const title =
    location.pathname.startsWith('/results')
      ? 'Diagnosis results'
      : location.pathname.startsWith('/comparison/')
        ? 'Model comparison'
        : pageTitles[location.pathname] || 'Clinical Consensus'

  return (
    <div className="app-shell min-h-screen">
      {menuOpen && (
        <button
          type="button"
          className="mobile-backdrop"
          aria-label="Close navigation"
          onClick={() => setMenuOpen(false)}
        />
      )}
      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <Activity size={20} strokeWidth={2.2} />
          </div>
          <div className="brand-copy">
            <strong>AI Consensus</strong>
            <span>Clinical decision support system</span>
          </div>
          <button
            type="button"
            className="icon-button sidebar-close"
            aria-label="Close navigation"
            onClick={() => setMenuOpen(false)}
          >
            <X size={19} />
          </button>
        </div>

        <div className="nav-section-label">Workspace</div>
        <nav className="primary-nav" aria-label="Main navigation">
          {navigation.map(({ label, to, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setMenuOpen(false)}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'nav-link-active' : ''}`
              }
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-card">
            <div className="connection-card-title">
              <span className="connection-indicator" />
              Service status
            </div>
            <StatusPill status={health} />
            <p>Live availability</p>
          </div>
          <div className="sidebar-footnote">
            <CertificationNotice />
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <div className="topbar-title">
            <button
              type="button"
              className="icon-button mobile-menu"
              aria-label="Open navigation"
              onClick={() => setMenuOpen(true)}
            >
              <Menu size={20} />
            </button>
            <div>
              <p className="breadcrumb">AI CONSENSUS CLINICAL DECISION SUPPORT</p>
              <h2>{title}</h2>
            </div>
          </div>
        </header>
        <main className="main-content">
          <Outlet
            context={{
              ...appContext,
              health,
            }}
          />
        </main>
      </div>
    </div>
  )
}
