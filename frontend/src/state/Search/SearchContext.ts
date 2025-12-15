import { createContext } from "react"
import type { FHIROrganization } from "../../@types/fhir"

// Define the search result structure
export interface SearchResult {
  data: FHIROrganization[] | null
  loading: boolean
  error: string | null
}

// Define the context value type
export interface SearchContextValue {
  searchResult: SearchResult
  searchByNameOrIdentifier: (nameOrId: string) => Promise<void>
  clearSearch: () => void
}

// Create the context with undefined default value
export const SearchContext = createContext<SearchContextValue | undefined>(
  undefined,
)
