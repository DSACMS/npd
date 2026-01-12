import { createContext } from "react"
import type { FHIROrganization, FHIRPractitioner } from "../../@types/fhir"

// Define the context value type
export interface SearchContextValue {
  initialQuery?: string
  data: FHIROrganization[] | FHIRPractitioner[] | null
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
export const SearchContext = createContext<SearchContextValue | undefined>(undefined)
export const SearchDispatchContext = createContext<
  SearchDispatchContextValue | undefined
>(undefined)
