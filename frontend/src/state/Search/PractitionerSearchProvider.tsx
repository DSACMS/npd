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
  const [isBackgroundLoading, setIsBackgroundLoading] = useState(false)
  const [params, setParams] = usePaginationParams()
  const [query, setQueryValue] = useState<string>(params.query || "")
  const { data, isLoading, error } = usePractitionersAPI(params, {
    requireQuery: true,
  })
  const pagination = usePagination(params, data)

  const buildParams = (overrides: { page?: string; query?: string; sort?: string }) => {
    const currentQuery = overrides.query ?? params.query ?? query
    const currentSort = overrides.sort ?? params.sort
    
    const next: Record<string, string> = {
      page: overrides.page ?? "1",
    }
    
    if (currentQuery) {
      next.query = currentQuery
    }
    
    if (currentSort) {
      next.sort = currentSort
    }
    
    return next
  }

  const setQuery = (nextQuery: string) => {
    setIsBackgroundLoading(false)
    setQueryValue(nextQuery)
    const next = buildParams({ page: "1", query: nextQuery })
    setParams(next, { preventScrollReset: true })
  }

  const navigateToPage = (toPage: number) => {
    setIsBackgroundLoading(true)
    const next = buildParams({ page: toPage.toString() })
    setParams(next, {
      preventScrollReset: true,
    })
  }

  const setSort = (nextSort: string) => {
    setIsBackgroundLoading(true)
    const next = buildParams({ page: "1", sort: nextSort })
    setParams(next, { preventScrollReset: true })
  }

  useEffect(() => {
    if (!isLoading) {
      setIsBackgroundLoading(false)
    }
  }, [isLoading])

  const hasActiveQuery = params.query && params.query.length > 0
  
  const state: SearchContextValue<FHIRPractioner> = {
    initialQuery: query,
    data: hasActiveQuery && data?.results?.entry
      ? data.results.entry.map((entry) => entry.resource)
      : null,
    isLoading,
    isBackgroundLoading,
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
    setSort,
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
