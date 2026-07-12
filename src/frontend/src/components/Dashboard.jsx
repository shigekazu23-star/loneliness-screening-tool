// ---- M7 Dashboard: latest score, trend chart, trend-linked message ----
// The message shown to the older adult follows the risk-flag design:
// supportive wording, "screening, not diagnosis" always visible.

import { ja } from '../i18n/ja.js'
import TrendChart from './TrendChart.jsx'

const TREND_TEXT = {
  rising: ja.trendRising,
  falling: ja.trendFalling,
  stable: ja.trendStable,
}

const FLAG_TEXT = {
  none: ja.flagNone,
  sustained_high: ja.flagSustainedHigh,
  worsening: ja.flagWorsening,
}

export default function Dashboard({ data, onAnswerAgain, onRevoke }) {
  const { history, trend, flag } = data
  const latest = history.length ? history[history.length - 1].score : null
  const flagged = flag.level !== 'none'

  return (
    <div className="card">
      <h2>{ja.dashboardTitle}</h2>
      {history.length === 0 ? (
        <p>{ja.noRecords}</p>
      ) : (
        <>
          <p>
            {ja.latestScore}: <span className="score-big">{latest}</span>
            <span className="note"> {ja.scoreRange}</span>
          </p>
          <p>
            {ja.trendLabel}: <strong>{TREND_TEXT[trend]}</strong>
          </p>
          <TrendChart history={history} />
          <p className={flagged ? 'status-warn' : 'status-ok'}>
            {FLAG_TEXT[flag.level]}
          </p>
        </>
      )}
      <p className="note">{ja.notDiagnosis}</p>
      <button className="secondary" onClick={onAnswerAgain}>
        {ja.answerAgain}
      </button>{' '}
      <button className="danger" onClick={onRevoke}>
        {ja.consentRevoke}
      </button>
    </div>
  )
}
