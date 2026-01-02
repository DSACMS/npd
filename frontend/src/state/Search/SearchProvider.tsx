import React, { useState, type ReactNode } from "react"
import { usePagination, usePaginationParams } from "../../hooks/usePagination"
import { useOrganizationsAPI } from "../requests/organizations"
import {
  SearchContext,
  SearchDispatchContext,
  type SearchContextValue,
  type SearchDispatchContextValue,
} from "./SearchContext"

interface SearchProviderProps {
  children: ReactNode
}

export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
  const [params, setParams] = usePaginationParams()
  const [query, setQueryValue] = useState<string>(params.query || "")
  const { data, isLoading, error } = useOrganizationsAPI(params, {
    requireQuery: true,
  })
  const pagination = usePagination(params, data)

  const setQuery = (nextQuery: string) => {
    setQueryValue(nextQuery)
    const next = { page: params.page.toString(), query: nextQuery }
    setParams(next, { preventScrollReset: true })
  }

  const navigateToPage = (toPage: number) => {
    const next = { page: toPage.toString(), query: query || params.query || "" }
    setParams(next, {
      preventScrollReset: true,
    })
  }

  const state: SearchContextValue = {
    initialQuery: query,
    data: data?.results?.entry
      ? data.results.entry.map((entry) => entry.resource)
      : null,
    isLoading,
    error: error
      ? error instanceof Error
        ? error.message
        : "An error occurred during search"
      : null,
    pagination,
    query,
  }

  const dispatch: SearchDispatchContextValue = {
    setQuery,
    navigateToPage,
    clearSearch: () => {
      setQueryValue("")
      setParams({})
    },
  }

  return (
    <SearchContext value={state}>
      <SearchDispatchContext value={dispatch}>{children}</SearchDispatchContext>
    </SearchContext>
  )
}
