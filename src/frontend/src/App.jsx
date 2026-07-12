// ---- Presentation layer root: role-based flow ----
// older_adult: login -> consent -> questionnaire -> dashboard
// caregiver:   login -> overview of consented, linked older adults

import { useCallback, useEffect, useState } from 'react'
import { api, setToken } from './api.js'
import { ja } from './i18n/ja.js'
import LoginView from './components/LoginView.jsx'
import ConsentView from './components/ConsentView.jsx'
import QuestionnaireView from './components/QuestionnaireView.jsx'
import Dashboard from './components/Dashboard.jsx'
import CaregiverView from './components/CaregiverView.jsx'

export default function App() {
  const [session, setSession] = useState(() => {
    const saved = sessionStorage.getItem('lst_session')
    return saved ? JSON.parse(saved) : null
  })
  const [consented, setConsented] = useState(null)
  const [view, setView] = useState('dashboard')
  const [historyData, setHistoryData] = useState(null)
  const [notice, setNotice] = useState('')

  function login(info) {
    sessionStorage.setItem('lst_session', JSON.stringify(info))
    setSession(info)
  }

  function logout() {
    setToken(null)
    sessionStorage.removeItem('lst_session')
    setSession(null)
    setConsented(null)
    setHistoryData(null)
    setNotice('')
  }

  const loadOlderAdult = useCallback(async () => {
    try {
      const status = await api.consentStatus()
      setConsented(status.active)
      if (status.active) {
        const data = await api.myHistory()
        setHistoryData(data)
        setView(data.history.length === 0 ? 'questionnaire' : 'dashboard')
      }
    } catch {
      logout()
    }
  }, [])

  useEffect(() => {
    if (session && session.role === 'older_adult') loadOlderAdult()
  }, [session, loadOlderAdult])

  async function revoke() {
    await api.revokeConsent()
    setConsented(false)
    setHistoryData(null)
    setNotice(ja.consentRevoked)
  }

  return (
    <div className="app">
      <div className="topbar">
        <div>
          <h1>{ja.appTitle}</h1>
          <p className="subtitle">{ja.appSubtitle}</p>
        </div>
        {session && (
          <button className="secondary" onClick={logout}>
            {ja.logout}
          </button>
        )}
      </div>

      {!session && <LoginView onLogin={login} />}

      {session && session.role === 'caregiver' && <CaregiverView />}

      {session && session.role === 'older_adult' && (
        <>
          {notice && <p className="status-ok">{notice}</p>}
          {consented === false && (
            <ConsentView
              onConsented={() => {
                setNotice('')
                loadOlderAdult()
              }}
            />
          )}
          {consented && view === 'questionnaire' && (
            <QuestionnaireView
              onSubmitted={async () => {
                const data = await api.myHistory()
                setHistoryData(data)
                setView('dashboard')
              }}
            />
          )}
          {consented && view === 'dashboard' && historyData && (
            <Dashboard
              data={historyData}
              onAnswerAgain={() => setView('questionnaire')}
              onRevoke={revoke}
            />
          )}
        </>
      )}
    </div>
  )
}
