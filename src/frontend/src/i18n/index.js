// ---- i18n runtime: language context and hook ----
// UI strings live in en.js / ja.js; components read them through useT().
// English is the default for coursework evaluation; the toggle in the
// top bar switches to the Japanese-first interface designed for end
// users. The choice persists across the session.

import { createContext, useContext } from 'react'
import { en } from './en.js'
import { ja } from './ja.js'

export const translations = { en, ja }

export const DEFAULT_LANG = 'en'

export const LangContext = createContext({
  lang: DEFAULT_LANG,
  setLang: () => {},
})

export function useT() {
  const { lang } = useContext(LangContext)
  return translations[lang]
}

export function useLang() {
  return useContext(LangContext)
}
