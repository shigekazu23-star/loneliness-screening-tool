// ---- M7 Dashboard: latest score, trend chart, trend-linked message ----
// The message shown to the older adult follows the risk-flag design:
// supportive wording, "screening, not diagnosis" always visible.

import { useT } from '../i18n/index.js'
import TrendChart from './TrendChart.jsx'

export default function Dashboard({ data, onAnswerAgain, onRevoke }) {
  const t = useT()
  const { history, trend, flag } = data
  const latest = history.length ? history[history.length - 1].score : null
  const flagged = flag.level !== 'none'

  const trendText = {
    rising: t.trendRising,
    falling: t.trendFalling,
    stable: t.trendStable,
  }
  const flagText = {
    none: t.flagNone,
    sustained_high: t.flagSustainedHigh,
    worsening: t.flagWorsening,
  }

  return (
    <div className="card">
      <h2>{t.dashboardTitle}</h2>
      {history.length === 0 ? (
        <p>{t.noRecords}</p>
      ) : (
        <>
          <p>
            {t.latestScore}: <span className="score-big">{latest}</span>
            <span className="note"> {t.scoreRange}</span>
          </p>
          <p>
            {t.trendLabel}: <strong>{trendText[trend]}</strong>
          </p>
          <TrendChart history={history} />
          <p className={flagged ? 'status-warn' : 'status-ok'}>
            {flagText[flag.level]}
          </p>
        </>
      )}
      <p className="note">{t.notDiagnosis}</p>
      <button className="secondary" onClick={onAnswerAgain}>
        {t.answerAgain}
      </button>{' '}
      <button className="danger" onClick={onRevoke}>
        {t.consentRevoke}
      </button>
    </div>
  )
}
