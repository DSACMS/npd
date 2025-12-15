import React, { useState, type ReactNode } from "react"
import { fetchOrganizations } from "../requests/organizations"
import {
  SearchContext,
  type SearchContextValue,
  type SearchResult,
} from "./SearchContext"

// Provider props
interface SearchProviderProps {
  children: ReactNode
}

// SearchProvider component
export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
  const [searchResult, setSearchResult] = useState<SearchResult>({
    data: null,
    loading: false,
    error: null,
  })

  const searchByNameOrIdentifier = async (nameOrId: string): Promise<void> => {
    if (!/^.+$/.test(nameOrId)) {
      setSearchResult({
        data: null,
        loading: false,
        error: "Search value must not be blank",
      })
      return
    }

    setSearchResult({
      data: null,
      loading: true,
      error: null,
    })

    try {
      const query: SearchParams = /^\d+$/.test(nameOrId)
        ? {
            identifier: nameOrId,
          }
        : { name: nameOrId }
      const data = await fetchOrganizations(query)

      const records = data.results.entry
        ? data.results.entry.map((entry) => entry.resource)
        : []

      setSearchResult({
        data: records,
        loading: false,
        error: null,
      })
    } catch (error) {
      setSearchResult({
        data: null,
        loading: false,
        error:
          error instanceof Error
            ? error.message
            : "An error occurred during search",
      })
    }
  }

  const clearSearch = (): void => {
    setSearchResult({
      data: null,
      loading: false,
      error: null,
    })
  }

  const value: SearchContextValue = {
    searchResult,
    searchByNameOrIdentifier,
    clearSearch,
  }

  return (
    <SearchContext.Provider value={value}>{children}</SearchContext.Provider>
  )
}
