import fhirOrganization from "./fhir_organization.json"

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: FhirOrganization =
  fhirOrganization as unknown as FhirOrganization
