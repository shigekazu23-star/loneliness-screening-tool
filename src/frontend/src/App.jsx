// ---- Presentation layer root: role-based flow and language provider ----
// older_adult: login -> consent -> questionnaire -> dashboard
// caregiver:   login -> overview of consented, linked older adults
// Language: English by default (evaluation), Japanese via the toggle
// (Japanese-first end-user design, strings externalized in i18n/).

import { useCallback, useEffect, useState } from 'react'
import { api, setToken } from './api.js'
import { DEFAULT_LANG, LangContext, translations } from './i18n/index.js'
import LoginView from './components/LoginView.jsx'
import ConsentView from './components/ConsentView.jsx'
import QuestionnaireView from './components/QuestionnaireView.jsx'
import Dashboard from './components/Dashboard.jsx'
import CaregiverView from './components/CaregiverView.jsx'

export default function App() {
  const [lang, setLang] = useState(
    () => sessionStorage.getItem('lst_lang') || DEFAULT_LANG,
  )
  const [session, setSession] = useState(() => {
    const saved = sessionStorage.getItem('lst_session')
    return saved ? JSON.parse(saved) : null
  })
  const [consented, setConsented] = useState(null)
  const [view, setView] = useState('dashboard')
  const [historyData, setHistoryData] = useState(null)
  const [notice, setNotice] = useState('')

  const t = translations[lang]

  function switchLang(next) {
    sessionStorage.setItem('lst_lang', next)
    setLang(next)
  }

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
    setNotice(t.consentRevoked)
  }

  return (
    <LangContext.Provider value={{ lang, setLang: switchLang }}>
      <div className="app">
        <div className="topbar">
          <div>
            <h1>{t.appTitle}</h1>
            <p className="subtitle">{t.appSubtitle}</p>
          </div>
          <div>
            <button
              className="linklike"
              onClick={() => switchLang(lang === 'en' ? 'ja' : 'en')}
              aria-label="Switch language"
            >
              {lang === 'en' ? '日本語' : 'English'}
            </button>{' '}
            {session && (
              <button className="secondary" onClick={logout}>
                {t.logout}
              </button>
            )}
          </div>
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
    </LangContext.Provider>
  )
}
