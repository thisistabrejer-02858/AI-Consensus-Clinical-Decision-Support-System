import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { RefreshCw } from 'lucide-react'
import { Button, Card, CardHeading, ErrorState, LoadingState, PageHeader } from '../components/UI'
import fixture from '../data/syntheticEvaluation.json'
import { evaluateCases } from '../services/api'
import { formatPercent } from '../utils/format'

function MetricCard({ label, value, note, isCount = false }) {
  const display = isCount ? String(value ?? '—') : formatPercent(value)
  return (
    <Card className="evaluation-metric">
      <span>{label}</span>
      <strong>{display}</strong>
      <small>{note}</small>
    </Card>
  )
}

export default function Evaluation() {
  const [refresh, setRefresh] = useState(0)
  const [state, setState] = useState({ loading: true, error: '', result: null })

  useEffect(() => {
    let active = true
    evaluateCases(fixture.cases)
      .then((result) => {
        if (active) setState({ loading: false, error: '', result })
      })
      .catch((error) => {
        if (active) setState({ loading: false, error: error.message, result: null })
      })
    return () => { active = false }
  }, [refresh])

  const rerun = () => {
    setState({ loading: true, error: '', result: null })
    setRefresh((value) => value + 1)
  }

  const result = state.result
  const chartData = result
    ? [
        { metric: 'Coverage', value: result.coverage_rate },
        { metric: 'Exact match', value: result.exact_match_rate },
        { metric: 'Model success', value: result.provider_success_rate },
        { metric: 'Mean agreement', value: result.mean_agreement_score },
      ]
    : []

  return (
    <>
      <PageHeader
        eyebrow="BENCHMARK"
        title="Evaluation & benchmarks"
        description="Review aggregate metrics calculated from the example test cases."
        action={
          <Button type="button" variant="secondary" onClick={rerun} disabled={state.loading}>
            <RefreshCw size={16} /> Re-run benchmark
          </Button>
        }
      />
      <div className="notice-banner info-banner">
        <span className="notice-icon">i</span>
        <p>These metrics describe only the included benchmark examples and should not be interpreted as clinical accuracy.</p>
      </div>
      {state.loading && <LoadingState label="Running the benchmark" />}
      {state.error && (
        <ErrorState
          title="Evaluation unavailable"
          message={state.error}
          action={<Button type="button" variant="secondary" onClick={rerun}>Try again</Button>}
        />
      )}
      {result && (
        <>
          <div className="evaluation-metrics">
            <MetricCard label="Total cases" value={result.total_cases} note={`${result.covered_cases} covered`} isCount />
            <MetricCard label="Coverage rate" value={result.coverage_rate} note="Cases with a predicted diagnosis" />
            <MetricCard label="Exact-match rate" value={result.exact_match_rate} note={`${result.exact_match_count} exact matches among covered cases`} />
            <MetricCard label="Model success" value={result.provider_success_rate} note="Across benchmark model attempts" />
          </div>
          <div className="content-grid results-grid">
            <Card>
              <CardHeading title="Returned evaluation metrics" description="Aggregate values returned by the backend." />
              <div className="chart-wrap evaluation-chart">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={chartData} margin={{ top: 8, right: 10, left: 0, bottom: 4 }}>
                    <CartesianGrid stroke="#edf0ec" vertical={false} />
                    <XAxis dataKey="metric" axisLine={false} tickLine={false} tick={{ fill: '#52645a', fontSize: 14 }} />
                    <YAxis domain={[0, 1]} axisLine={false} tickLine={false} tick={{ fill: '#52645a', fontSize: 14 }} tickFormatter={(value) => `${Math.round(value * 100)}%`} />
                    <Tooltip formatter={(value) => [formatPercent(value), 'Value']} />
                    <Bar dataKey="value" fill="#668278" radius={[5, 5, 0, 0]} barSize={34} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="evaluation-note">{result.evaluation_note}</p>
            </Card>
            <Card>
              <CardHeading title="Mean agreement" description="Average input agreement score reported by the evaluation service." />
              <div className="evaluation-highlight">
                <strong>{formatPercent(result.mean_agreement_score)}</strong>
                <span>Alignment indicator, not diagnostic accuracy.</span>
              </div>
            </Card>
          </div>
          <Card className="fixture-card">
            <CardHeading
              title="Example test cases"
              description="These are the input labels sent to the aggregate evaluator. The endpoint does not return per-case evaluation results."
            />
            <div className="comparison-table-wrap">
              <table className="data-table">
                <thead><tr><th scope="col">Expected label</th><th scope="col">Predicted input</th><th scope="col">Model successes</th><th scope="col">Input agreement</th></tr></thead>
                <tbody>
                  {fixture.cases.map((item, index) => (
                    <tr key={`${item.expected_diagnosis}-${index}`}>
                      <td><strong>{item.expected_diagnosis}</strong></td>
                      <td>{item.predicted_diagnosis || 'No prediction'}</td>
                      <td>{item.provider_successes} / {item.provider_count}</td>
                      <td>{formatPercent(item.agreement_score)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </>
  )
}
