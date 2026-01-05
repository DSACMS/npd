import { skipToken, useQuery } from "@tanstack/react-query"
import type { FHIRCollection, FHIRPractioner } from "../../@types/fhir"
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

const detectQueryKey = (value: string): "identifier" | "name" => {
  return /^\d+$/.test(value) ? "identifier" : "name"
}

/// list

export const fetchPractitioners = async (
  params: PaginationParams & SearchParams,
): Promise<FHIRCollection<FHIRPractioner>> => {
  const url = new URL(apiUrl("/fhir/Practitioner/"))

  // Pagination
  if (params.page) {
    url.searchParams.set("page", params.page.toString())
  }
  if (params.page_size) {
    url.searchParams.set("page_size", params.page_size.toString())
  }

  // Search
  if (params.query) {
    const query = params.query
    const key = detectQueryKey(query)
    url.searchParams.set(key, query)
  }

  const response = await fetch(url)
  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json()
}

type QueryOptions = {
  enabled?: boolean
  requireQuery?: boolean
}

export const usePractitionersAPI = (
  params: PaginationParams & SearchParams,
  options?: QueryOptions,
) => {
  console.debug("[usePractitionersAPI]", { params, options })

  return useQuery<FHIRCollection<FHIRPractioner>>({
    queryKey: ["practitioners", params.query, params.page || 1],
    queryFn:
      options?.requireQuery && (!params.query || params.query.length === 0)
        ? skipToken
        : () => {
            return fetchPractitioners(params)
          },
  })
}

