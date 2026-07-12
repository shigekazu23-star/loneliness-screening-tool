// ---- API client: single place where the frontend talks to the Flask API ----

let token = sessionStorage.getItem('lst_token') || null

export function setToken(value) {
  token = value
  if (value) sessionStorage.setItem('lst_token', value)
  else sessionStorage.removeItem('lst_token')
}

async function call(method, path, body) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`)
  return data
}

export const api = {
  register: (payload) => call('POST', '/api/register', payload),
  login: (payload) => call('POST', '/api/login', payload),
  consentStatus: () => call('GET', '/api/consent'),
  grantConsent: () => call('POST', '/api/consent'),
  revokeConsent: () => call('DELETE', '/api/consent'),
  submitResponse: (answers) => call('POST', '/api/responses', answers),
  myHistory: () => call('GET', '/api/responses'),
  linkOlderAdult: (username) =>
    call('POST', '/api/caregiver/link', { username }),
  caregiverOverview: () => call('GET', '/api/caregiver/overview'),
}
