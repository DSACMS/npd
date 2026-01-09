import { createContext } from "react"
import type { FHIROrganization, FHIRPractioner } from "../../@types/fhir"

// Define the context value type
export interface SearchContextValue<T> {
  initialQuery?: string
  data: T[] | null
  isLoading: boolean
  isBackgroundLoading: boolean
  error: string | null
  pagination?: PaginationState
  query?: string
}

export interface SearchDispatchContextValue {
  setQuery: (nameOrId: string) => void
  navigateToPage: (page: number) => void
  setSort: (sort: string) => void
  clearSearch: () => void
}

// Create the context with undefined default value
export const OrganizationSearchContext = createContext<SearchContextValue<FHIROrganization> | undefined>(
  undefined,
)
export const PractitionerSearchContext = createContext<SearchContextValue<FHIRPractioner> | undefined>(
  undefined,
)
export const SearchDispatchContext = createContext<
  SearchDispatchContextValue | undefined
>(undefined)
