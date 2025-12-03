import { useQuery } from "@tanstack/react-query"
import { apiUrl } from "../api"
import { formatAddress} from "../../helpers/org_helpers"

const fetchOrganization = async (
  organizationId: string,
): Promise<FhirOrganization> => {
  const url = apiUrl("/fhir/Organization/:organizationId/", { organizationId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FhirOrganization>
}

export const useOrganizationAPI = (organizationId: string | undefined) => {
  return useQuery<FhirOrganization>({
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

export const organizationNpiSelector = (org?: FhirOrganization) => {
  if (!org) return ""

  if (!org.identifier.length) {
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