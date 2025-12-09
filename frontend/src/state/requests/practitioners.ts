import { useQuery } from "@tanstack/react-query"
import type { FHIRPractioner } from "../../@types/fhir"
import { apiUrl } from "../api"
import { formatAddress } from "../../helpers/org_helpers"

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically

const fetchPractitioner = async (
  practitionerId: string,
): Promise<FHIRPractioner> => {
  const url = apiUrl("/fhir/Practitioner/:practitionerId/", { practitionerId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRPractioner>
}

export const usePractitionerAPI = (practitionerId: string | undefined) => {
  return useQuery<FHIRPractioner>({
    queryKey: ["practitioner", practitionerId],
    queryFn: () => {
      if (!practitionerId) {
        return Promise.reject("no practitionerId was provided")
      }

      return fetchPractitioner(practitionerId)
    },
  })
}

////
// Selectors unpack the API responses
////

export const practitionerNameSelector = (
  record: FHIRPractioner,
): string | null => {
  if (!record.name || record.name?.length === 0) return "No name available"

  const name = record.name[0]

  return name.text || ""
}

export const practitionerAddressSelector = (
  record: FHIRPractioner,
): string | null => {
  if (!record || !record.address?.length) return ""

  const contact = record.address[0]
  if (!contact) return ""

  return formatAddress(contact)
}

export const practitionerGenderSelector = (
  record: FHIRPractioner,
): string | null => {
  return record?.gender ?? null
}

export const practitionerDeceasedSelector = (
  record: FHIRPractioner,
): string | null => {
  return record.deceasedBoolean ? "Yes" : "No"
}

export const practitionerActiveSelector = (
  record: FHIRPractioner,
): string | null => {
  return record.active ? "Yes" : "No"
}

export const practitionerPhoneSelector = ( //use logic to find phone specifically throught system === phone
  record: FHIRPractioner,
): string | null => {
  if (!record || record.telecom?.length) return ""

  const contact = record.telecom?.[0]
  return contact?.value ?? null
}

export const practitionerFaxSelector = ( //use logic to find phone specifically throught system === fax
  record: FHIRPractioner,
): string | null => {
  if (!record || record.telecom?.length) return ""

  const contact = record.telecom?.[0]
  return contact?.value ?? null
}