import { ArrowRight, BookOpen, Database, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Card, CardHeading, PageHeader } from '../components/UI'

export default function About() {
  return (
    <>
      <PageHeader
        eyebrow="ABOUT THE SYSTEM"
        title="AI Consensus Clinical Decision Support System"
        description="A multi-model system that brings AI-generated clinical case summaries together for review."
      />
      <Card className="about-intro">
        <div className="about-icon"><BookOpen size={21} /></div>
        <div>
          <span className="eyebrow">MULTI-MODEL AI CONSENSUS</span>
          <h2>Bring multiple AI perspectives together.</h2>
          <p>Review candidate summaries and areas of agreement or disagreement from multiple AI models in one place.</p>
          <Link className="button button-primary about-start-link" to="/new-case">
            Start a new analysis <ArrowRight size={17} />
          </Link>
        </div>
      </Card>
      <div className="about-user-grid">
        <Card>
          <CardHeading title="Your history stays in this browser" />
          <div className="about-info-row">
            <span className="about-info-icon"><Database size={19} /></span>
            <p>No sign-in or patient database is used. Saved analysis summaries stay in this browser on this device; clearing browser data removes them.</p>
          </div>
          <Link to="/history" className="text-link">View your saved analyses <ArrowRight size={16} /></Link>
        </Card>
        <Card className="about-safety-card">
          <span className="about-info-icon"><ShieldCheck size={19} /></span>
          <div>
            <CardHeading title="Understanding model agreement" />
            <p>Agreement indicates how closely model outputs align. It does not confirm that a diagnosis is correct.</p>
          </div>
        </Card>
      </div>
    </>
  )
}
