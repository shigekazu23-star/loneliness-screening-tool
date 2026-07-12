// ---- M3 Questionnaire UI: Three-Item Loneliness Scale ----
// One large radio group per item; a response cannot be sent until all
// three items are answered (client-side mirror of the M3 validation).

import { useState } from 'react'
import { api } from '../api.js'
import { useT } from '../i18n/index.js'

export default function QuestionnaireView({ onSubmitted }) {
  const t = useT()
  const [answers, setAnswers] = useState({})
  const [error, setError] = useState('')

  const items = [
    { key: 'q1', text: t.q1 },
    { key: 'q2', text: t.q2 },
    { key: 'q3', text: t.q3 },
  ]
  const options = [
    { value: 1, text: t.answer1 },
    { value: 2, text: t.answer2 },
    { value: 3, text: t.answer3 },
  ]

  async function submit() {
    if (items.some((item) => !answers[item.key])) {
      setError(t.answerAllItems)
      return
    }
    setError('')
    try {
      const result = await api.submitResponse(answers)
      onSubmitted(result)
    } catch {
      setError(t.errorGeneric)
    }
  }

  return (
    <div className="card">
      <h2>{t.questionnaireTitle}</h2>
      <p>{t.questionnaireLead}</p>
      {items.map((item) => (
        <fieldset key={item.key} style={{ border: 'none', padding: 0 }}>
          <legend style={{ fontWeight: 700, padding: 0 }}>{item.text}</legend>
          <div className="choice-group">
            {options.map((answer) => (
              <label
                key={answer.value}
                className={`choice ${
                  answers[item.key] === answer.value ? 'selected' : ''
                }`}
              >
                <input
                  type="radio"
                  name={item.key}
                  checked={answers[item.key] === answer.value}
                  onChange={() =>
                    setAnswers({ ...answers, [item.key]: answer.value })
                  }
                />
                {answer.text}
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      {error && <p className="error">{error}</p>}
      <button onClick={submit}>{t.submitAnswers}</button>
    </div>
  )
}
