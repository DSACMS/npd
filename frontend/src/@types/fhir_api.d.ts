///
// /fhir/Organization/:id
///

interface Identifier {
  use: string
  type: {
    coding: Coding[]
  }
  system: string
  value: string
  period: {
    start: string
  }
}

interface Coding {
  system: string
  code: string
  display: string
}

interface Address {
  line: string[]
  city: string
  state: string
  postalCode: string
  country: string
}

interface Contact {
  name: ContactName
  telecom: Telecom[]
  address?: Address
}

interface ContactName {
  use: string
  text: string
  family: string
  given: (string | null)[]
  prefix: (string | null)[]
  suffix: (string | null)[]
  period: Record<string, never> // Empty object
}

interface Telecom {
  system: string
  value: string
  use: string
}

interface FhirOrganization {
  resourceType: "Organization"
  id: string
  meta: {
    profile: string[]
  }
  identifier: Identifier[]
  name: string
  contact: Contact[]
}
