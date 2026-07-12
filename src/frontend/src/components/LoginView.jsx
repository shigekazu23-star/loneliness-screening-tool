import { useState } from 'react'
import { api, setToken } from '../api.js'
import { useT } from '../i18n/index.js'

export default function LoginView({ onLogin }) {
  const t = useT()
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [role, setRole] = useState('older_adult')
  const [error, setError] = useState('')

  async function submit(event) {
    event.preventDefault()
    setError('')
    try {
      if (mode === 'register') {
        await api.register({
          username,
          password,
          role,
          display_name: displayName || username,
        })
      }
      const data = await api.login({ username, password })
      setToken(data.token)
      onLogin({ role: data.role, displayName: data.display_name })
    } catch (err) {
      setError(mode === 'login' ? t.errorLogin : err.message)
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>{mode === 'login' ? t.login : t.register}</h2>
      <label htmlFor="username">{t.username}</label>
      <input
        id="username"
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        autoComplete="username"
      />
      <label htmlFor="password">{t.password}</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        autoComplete="current-password"
      />
      {mode === 'register' && (
        <>
          <label htmlFor="displayName">{t.displayName}</label>
          <input
            id="displayName"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
          <label>{t.roleLabel}</label>
          <div className="choice-group">
            <label
              className={`choice ${role === 'older_adult' ? 'selected' : ''}`}
            >
              <input
                type="radio"
                name="role"
                checked={role === 'older_adult'}
                onChange={() => setRole('older_adult')}
              />
              {t.roleOlderAdult}
            </label>
            <label
              className={`choice ${role === 'caregiver' ? 'selected' : ''}`}
            >
              <input
                type="radio"
                name="role"
                checked={role === 'caregiver'}
                onChange={() => setRole('caregiver')}
              />
              {t.roleCaregiver}
            </label>
          </div>
        </>
      )}
      {error && <p className="error">{error}</p>}
      <button type="submit">
        {mode === 'login' ? t.loginButton : t.registerButton}
      </button>
      <div>
        <button
          type="button"
          className="linklike"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? t.switchToRegister : t.switchToLogin}
        </button>
      </div>
    </form>
  )
}
