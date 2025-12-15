import { useMemo } from "react"
import { useSearchParams } from "react-router"
import type { FHIRCollection } from "../@types/fhir"

const DEFAULT_PAGE_SIZE = 10

const toInt = (value: string | null | undefined, fallback: number): number => {
  if (typeof value === "undefined" || value === null) return fallback

  const pval = parseInt(value)
  return isNaN(pval) ? fallback : pval
}

const coercePaginationParams = (
  params: URLSearchParams,
): RequiredPaginationParams => {
  return {
    page: toInt(params.get("page"), 1),
    page_size: toInt(params.get("page_size"), DEFAULT_PAGE_SIZE),
  }
}

export const usePaginationParams = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [search, _setSearch] = useSearchParams()
  return coercePaginationParams(search)
}

export const usePagination = (
  pagination: RequiredPaginationParams,
  data: undefined | FHIRCollection<unknown>,
): PaginationState => {
  return useMemo(() => {
    let totalPages = 1
    let total = 0
    let count = 0

    if (data) {
      totalPages = Math.ceil(data.count / pagination.page_size)
      total = data.results.total
      count = data.count
    }

    return {
      ...pagination,
      total,
      count,
      totalPages,
    }
  }, [data, pagination])
}
