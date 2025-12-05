import type { Organization } from "../../src/@types/fhir/Organization"
import fhirOrganization from "./fhir_organization.json"

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: Organization = fhirOrganization
