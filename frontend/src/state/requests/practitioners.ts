import { useQuery } from "@tanstack/react-query"
import type { FHIRPractioner } from "../../@types/fhir"
import { apiUrl } from "../api"

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
