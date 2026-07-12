// ---- Caregiver view: RBAC-limited, consent-gated overview ----
// Shows only older adults who are linked AND hold an active consent.
// Revocation on the older adult's side removes the card immediately.

import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { useT } from '../i18n/index.js'
import TrendChart from './TrendChart.jsx'

export default function CaregiverView() {
  const t = useT()
  const [people, setPeople] = useState([])
  const [username, setUsername] = useState('')
  const [error, setError] = useState('')

  async function refresh() {
    const data = await api.caregiverOverview()
    setPeople(data.people)
  }

  useEffect(() => {
    refresh()
  }, [])

  async function link(event) {
    event.preventDefault()
    setError('')
    try {
      await api.linkOlderAdult(username)
      setUsername('')
      await refresh()
    } catch (err) {
      setError(err.message || t.errorGeneric)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>{t.caregiverTitle}</h2>
        <p>{t.caregiverLead}</p>
        <form onSubmit={link}>
          <label htmlFor="link-username">{t.linkPlaceholder}</label>
          <input
            id="link-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit">{t.linkButton}</button>
        </form>
      </div>
      {people.length === 0 && (
        <div className="card">
          <p>{t.noLinkedPeople}</p>
        </div>
      )}
      {people.map((person) => {
        const flagged = person.flag.level !== 'none'
        return (
          <div className="card person-card" key={person.username}>
            <h3>{person.display_name}</h3>
            <p>
              {t.lastScoreLabel}:{' '}
              <span className="score-big">{person.latest_score ?? '—'}</span>
            </p>
            <p className={flagged ? 'status-warn' : 'status-ok'}>
              {t.attentionLabel}:{' '}
              {flagged ? t.attentionNeeded : t.noAttention}
            </p>
            <TrendChart history={person.history} />
          </div>
        )
      })}
    </div>
  )
}
