import { useQuery } from "@tanstack/react-query"
import type { Address } from "../../@types/fhir/Address"
import type { Identifier } from "../../@types/fhir/Identifier"
import type { Organization as FhirOrganization } from "../../@types/fhir/Organization"
import { apiUrl } from "../api"
import { formatAddress, formatDate } from "../../helpers/org_helpers"

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically
export interface Organization extends FhirOrganization {
  identifier?: Identifier[] | null
  address?: Address[] | null
}

const fetchOrganization = async (
  organizationId: string,
): Promise<Organization> => {
  const url = apiUrl("/fhir/Organization/:organizationId/", { organizationId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<Organization>
}

export const useOrganizationAPI = (organizationId: string | undefined) => {
  return useQuery<Organization>({
    queryKey: ["organization", organizationId],
    queryFn: () => {
      if (!organizationId) {
        return Promise.reject("no organizationId was provided")
      }

      return fetchOrganization(organizationId)
    },
  })
}

////
// Selectors unpack the API responses
////

export const organizationNpiSelector = (org?: Organization) => {
  if (!org) return ""

  if (!org.identifier?.length) {
    return "n/a"
  }

  const npiIdentifier = org.identifier.find(
    (ident) => ident.system === "http://terminology.hl7.org/NamingSystem/npi",
  )

  return npiIdentifier?.value || "n/a"
}

export const organizationMailingAddressSelector = (org?: FhirOrganization) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  if (!contact.address) return ""

  return formatAddress(contact.address)
}

export const organizationAuthorizedOfficialSelector = (
  org?: FhirOrganization,
) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  if (!contact.name) return ""

  return contact.name.text
}

export const organizationAuthorizedPhoneSelector = (org?: FhirOrganization) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  const phone = contact.telecom?.find((t) => t.system === "phone")

  return phone?.value || ""
}

export const organizationIdentifiersSelector = (org?: FhirOrganization) => {
  if (!org || !org.identifier.length) return []

  return org.identifier.map((identity) => ({
    type: identity.type?.coding?.[0]?.display || "Unknown",
    number: identity.value,
    details: identity.period?.start
      ? `Active, Received ${formatDate(identity.period.start)}` // hardcoding active and recieved if we get a response?
      : "",
    system: identity.system,
  }))
}