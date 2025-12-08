// components
import errors from "./errors.json"
import footer from "./footer.json"
import header from "./header.json"

// pages
import developers from "./developers.json"
import landing from "./landing.json"
import organizations from "./organizations.json"

/*
 * NOTE: (@abachman-dsac) a word about i18n usage in react components and the
 * names of keys
 *
 * Keys definied here use the root-level key shown below plus whatever hierarchy
 * is defined in the corresponding JSON file.
 *
 * For example, given header.json:
 *
 *   { "section": { "title": "Blah Section" } }
 *
 * The TFunction would reference that value with:
 *
 *   t('header.section.title')
 *
 * Due to the use of `header` in the `translations` object here, and the direct
 * handing of `translations` to the i18n configuration.
 *
 * Also, the use of "translations" as the defaultNS in i18n.ts necessitates its
 * use here.
 */
export const translations = {
  header,
  footer,
  landing,
  developers,
  errors,
  organizations
}
