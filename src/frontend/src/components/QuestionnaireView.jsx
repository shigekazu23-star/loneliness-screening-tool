// ---- M3 Questionnaire UI: Three-Item Loneliness Scale ----
// One large radio group per item; a response cannot be sent until all
// three items are answered (client-side mirror of the M3 validation).

import { useState } from 'react'
import { api } from '../api.js'
import { ja } from '../i18n/ja.js'

const ITEMS = [
  { key: 'q1', text: ja.q1 },
  { key: 'q2', text: ja.q2 },
  { key: 'q3', text: ja.q3 },
]
const ANSWERS = [
  { value: 1, text: ja.answer1 },
  { value: 2, text: ja.answer2 },
  { value: 3, text: ja.answer3 },
]

export default function QuestionnaireView({ onSubmitted }) {
  const [answers, setAnswers] = useState({})
  const [error, setError] = useState('')

  async function submit() {
    if (ITEMS.some((item) => !answers[item.key])) {
      setError(ja.answerAllItems)
      return
    }
    setError('')
    try {
      const result = await api.submitResponse(answers)
      onSubmitted(result)
    } catch {
      setError(ja.errorGeneric)
    }
  }

  return (
    <div className="card">
      <h2>{ja.questionnaireTitle}</h2>
      <p>{ja.questionnaireLead}</p>
      {ITEMS.map((item) => (
        <fieldset key={item.key} style={{ border: 'none', padding: 0 }}>
          <legend style={{ fontWeight: 700, padding: 0 }}>{item.text}</legend>
          <div className="choice-group">
            {ANSWERS.map((answer) => (
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
      <button onClick={submit}>{ja.submitAnswers}</button>
    </div>
  )
}
