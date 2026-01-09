import { useContext } from "react"
import {
  PractitionerSearchContext,
  OrganizationSearchContext,
  SearchDispatchContext,
  type SearchContextValue,
  type SearchDispatchContextValue,
} from "./SearchContext"
import type { FHIROrganization, FHIRPractioner } from "../../@types/fhir"

// Custom hook to use the search context
export const usePractitionerSearchState = (): SearchContextValue<FHIRPractioner> => {
  const context = useContext(PractitionerSearchContext)
  if (context === undefined) {
    throw new Error("useSearchState must be used within a SearchProvider")
  }
  return context
}

export const useOrganizationSearchState = (): SearchContextValue<FHIROrganization> => {
  const context = useContext(OrganizationSearchContext)
  if (context === undefined) {
    throw new Error("useSearchState must be used within a SearchProvider")
  }
  return context
}

// Custom hook to use the search context
export const useSearchDispatch = (): SearchDispatchContextValue => {
  const context = useContext(SearchDispatchContext)
  if (context === undefined) {
    throw new Error("useSearchDispatch must be used within a SearchProvider")
  }
  return context
}
