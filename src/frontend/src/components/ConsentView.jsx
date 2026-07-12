// ---- M2 Consent UI: explicit opt-in in plain language ----

import { api } from '../api.js'
import { useT } from '../i18n/index.js'

export default function ConsentView({ onConsented }) {
  const t = useT()

  async function agree() {
    await api.grantConsent()
    onConsented()
  }

  return (
    <div className="card">
      <h2>{t.consentTitle}</h2>
      <p>{t.consentBody}</p>
      <button onClick={agree}>{t.consentAgree}</button>
    </div>
  )
}
