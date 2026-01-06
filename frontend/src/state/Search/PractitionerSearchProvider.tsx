import React, { useEffect, useState, type ReactNode } from "react"
import { usePagination, usePaginationParams } from "../../hooks/usePagination"
import { usePractitionersAPI } from "../requests/practitioners"
import {
  PractitionerSearchContext,
  SearchDispatchContext,
  type SearchContextValue,
  type SearchDispatchContextValue,
} from "./SearchContext"
import type { FHIRPractioner } from "../../@types/fhir"

interface SearchProviderProps {
  children: ReactNode
}

export const PractitionerSearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
  const [isPaging, setIsPaging] = useState(false)
  const [params, setParams] = usePaginationParams()
  const [query, setQueryValue] = useState<string>(params.query || "")
  const { data, isLoading, error } = usePractitionersAPI(params, {
    requireQuery: true,
  })
  const pagination = usePagination(params, data)

  const setQuery = (nextQuery: string) => {
    setIsPaging(false)
    setQueryValue(nextQuery)
    const next = { page: "1", query: nextQuery }
    setParams(next, { preventScrollReset: true })
  }

  const navigateToPage = (toPage: number) => {
    setIsPaging(true)
    const next = { page: toPage.toString(), query: params.query || query || "" }
    setParams(next, {
      preventScrollReset: true,
    })
  }

  useEffect(() => {
    if (!isLoading) {
      setIsPaging(false)
    }
  }, [isLoading])

  const state: SearchContextValue<FHIRPractioner> = {
    initialQuery: query,
    data: data?.results?.entry
      ? data.results.entry.map((entry) => entry.resource)
      : null,
    isLoading,
    isPaging,
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
    <PractitionerSearchContext value={state}>
      <SearchDispatchContext value={dispatch}>{children}</SearchDispatchContext>
    </PractitionerSearchContext>
  )
}
