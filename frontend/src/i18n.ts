import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

import { translations } from "./i18n/en"

export const defaultNS = "translations"
export const resources = {
  en: {
    translations,
  },
} as const

// run `npm run dev` with DEBUG_I18N=1 set to get i18next debugging
const debug = !!import.meta.env.DEBUG_I18N

i18n
  // detect user language
  // learn more: https://github.com/i18next/i18next-browser-languageDetector
  .use(LanguageDetector)
  // pass the i18n instance to react-i18next.
  .use(initReactI18next)
  // init i18next
  // for all options read: https://www.i18next.com/overview/configuration-options
  .init({
    lng: "en",
    supportedLngs: ["en"],
    fallbackLng: "en",
    debug,
    defaultNS,
    resources,
    interpolation: {
      escapeValue: false, // not needed for react as it escapes by default
    },
  })

export default i18n
