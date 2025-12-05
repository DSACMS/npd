import { useQuery } from "@tanstack/react-query"
import type { HumanName } from "../../@types/fhir/HumanName"
import type { Identifier } from "../../@types/fhir/Identifier"
import type { Practitioner as FhirPractitioner } from "../../@types/fhir/Practitioner"
import { apiUrl } from "../api"

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically
export interface Practitioner extends FhirPractitioner {
  name?: HumanName[] | null
  identifier?: Identifier[] | null
}

const fetchPractitioner = async (
  practitionerId: string,
): Promise<Practitioner> => {
  const url = apiUrl("/fhir/Practitioner/:practitionerId/", { practitionerId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<Practitioner>
}

export const usePractitionerAPI = (practitionerId: string | undefined) => {
  return useQuery<Practitioner>({
    queryKey: ["practitioner", practitionerId],
    queryFn: () => {
      console.log("fetch practitioner?", practitionerId)
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
  record: Practitioner,
): string | null => {
  if (!record.name || record.name?.length === 0) return null

  const name: HumanName = record.name[0] as unknown as HumanName

  return name.text || ""
}
