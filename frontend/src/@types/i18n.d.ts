import { defaultNS, resources } from "../i18n"

// NOTE: (@abachman-dsac) this is based on documentation from
// https://www.i18next.com/overview/typescript#create-a-declaration-file

declare module "i18next" {
  interface CustomTypeOptions {
    defaultNS: typeof defaultNS
    resources: typeof resources
    strictKeyChecks: true
  }
}
