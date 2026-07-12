// ---- M2 Consent UI: explicit opt-in in plain language ----

import { api } from '../api.js'
import { ja } from '../i18n/ja.js'

export default function ConsentView({ onConsented }) {
  async function agree() {
    await api.grantConsent()
    onConsented()
  }

  return (
    <div className="card">
      <h2>{ja.consentTitle}</h2>
      <p>{ja.consentBody}</p>
      <button onClick={agree}>{ja.consentAgree}</button>
    </div>
  )
}
