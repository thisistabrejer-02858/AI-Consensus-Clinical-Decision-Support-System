import { useEffect, useState } from 'react'
import { lazy, Suspense } from 'react'
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom'
import AppLayout from './components/AppLayout'
import useHistory from './hooks/useHistory'

const About = lazy(() => import('./pages/About'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Evaluation = lazy(() => import('./pages/Evaluation'))
const History = lazy(() => import('./pages/History'))
const ModelComparison = lazy(() => import('./pages/ModelComparison'))
const NewCase = lazy(() => import('./pages/NewCase'))
const Results = lazy(() => import('./pages/Results'))

function ScrollToTop() {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return null
}

export default function App() {
  const historyState = useHistory()
  const [activeResult, setActiveResult] = useState(null)
  const appContext = {
    ...historyState,
    activeResult,
    setActiveResult,
  }

  return (
    <BrowserRouter>
      <ScrollToTop />
      <Suspense fallback={<div className="app-loading" role="status">Loading workspace…</div>}>
        <Routes>
          <Route element={<AppLayout appContext={appContext} />}>
            <Route index element={<Dashboard />} />
            <Route path="new-case" element={<NewCase />} />
            <Route path="results" element={<Results />} />
            <Route path="results/:analysisId" element={<Results />} />
            <Route path="history" element={<History />} />
            <Route path="comparison" element={<ModelComparison />} />
            <Route
              path="comparison/:analysisId"
              element={<ModelComparison />}
            />
            <Route path="evaluation" element={<Evaluation />} />
            <Route path="about" element={<About />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
