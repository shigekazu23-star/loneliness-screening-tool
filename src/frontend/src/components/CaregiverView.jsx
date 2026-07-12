// ---- Caregiver view: RBAC-limited, consent-gated overview ----
// Shows only older adults who are linked AND hold an active consent.
// Revocation on the older adult's side removes the card immediately.

import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { ja } from '../i18n/ja.js'
import TrendChart from './TrendChart.jsx'

export default function CaregiverView() {
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
      setError(err.message || ja.errorGeneric)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>{ja.caregiverTitle}</h2>
        <p>{ja.caregiverLead}</p>
        <form onSubmit={link}>
          <label htmlFor="link-username">{ja.linkPlaceholder}</label>
          <input
            id="link-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit">{ja.linkButton}</button>
        </form>
      </div>
      {people.length === 0 && (
        <div className="card">
          <p>{ja.noLinkedPeople}</p>
        </div>
      )}
      {people.map((person) => {
        const flagged = person.flag.level !== 'none'
        return (
          <div className="card person-card" key={person.username}>
            <h3>{person.display_name}</h3>
            <p>
              {ja.lastScoreLabel}:{' '}
              <span className="score-big">{person.latest_score ?? '—'}</span>
            </p>
            <p className={flagged ? 'status-warn' : 'status-ok'}>
              {ja.attentionLabel}:{' '}
              {flagged ? ja.attentionNeeded : ja.noAttention}
            </p>
            <TrendChart history={person.history} />
          </div>
        )
      })}
    </div>
  )
}
