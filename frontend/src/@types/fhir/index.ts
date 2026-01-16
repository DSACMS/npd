import type { Address } from "./Address"
import type { Identifier } from "./Identifier"
import type { Organization } from "./Organization"
import type { CodeableConcept } from "./CodeableConcept"
import type { Period } from "./Period"
import type { Coding } from "./Coding"
import type { ExtendedContactDetail } from "./ExtendedContactDetail"
import type { Practitioner  } from "./Practitioner"
import type { HumanName } from "./HumanName"
import type { ContactPoint } from "./ContactPoint"

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically
export interface FHIROrganization extends Organization {
    identifier?: FHIRIdentifer[] | null
    contact?: ExtendedContactDetail[] | null
    address?: Address[] | null
}

export interface FHIRIdentifer extends Identifier {
    type?: FHIRCodeableConcept
    period?: Period
}

export interface FHIRCodeableConcept extends CodeableConcept {
    coding?: Coding[]
}

export interface FHIRPractioner extends Practitioner {
    name?: HumanName[] | null
    identifier?: FHIRIdentifer[] | null
    telecom?: ContactPoint[] | null
}