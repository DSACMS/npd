import { useQuery } from "@tanstack/react-query"
import { apiUrl } from "../api"
import { formatAddress, formatDate } from "../../helpers/formatters"
import type { FHIROrganization } from "../../@types/fhir"

const fetchOrganization = async (
  organizationId: string,
): Promise<FHIROrganization> => {
  const url = apiUrl("/fhir/Organization/:organizationId/", { organizationId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIROrganization>
}

export const useOrganizationAPI = (organizationId: string | undefined) => {
  return useQuery<FHIROrganization>({
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

export const organizationNpiSelector = (
  org?: Pick<FHIROrganization, "identifier">,
) => {
  if (!org) return ""

  if (!org.identifier?.length) {
    return "n/a"
  }

  const npiIdentifier = org.identifier.find(
    (ident) =>
      ident.system === "http://terminology.hl7.org/NamingSystem/npi" ||
      ident.system === "http://hl7.org/fhir/sid/us-npi",
  )

  return npiIdentifier?.value || "n/a"
}

export const organizationMailingAddressSelector = (org?: FHIROrganization) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  if (!contact.address) return ""

  return formatAddress(contact.address)
}

export const organizationAuthorizedOfficialSelector = (
  org?: FHIROrganization,
) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  if (!contact.name) return ""

  return contact.name.text
}

export const organizationAuthorizedPhoneSelector = (org?: FHIROrganization) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  const phone = contact?.telecom?.find((t) => t.system === "phone")

  return phone?.value || ""
}

export const organizationIdentifiersSelector = (org?: FHIROrganization) => {
  if (!org || !org.identifier?.length) return []

  return org.identifier.map((identity) => ({
    type: identity.type?.coding?.[0]?.display || "Unknown",
    number: identity.value,
    details: identity.period?.start
      ? `Active, Received ${formatDate(identity.period.start)}` // hardcoding active and recieved if we get a response?
      : "",
    system: identity.system,
  }))
}