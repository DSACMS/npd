import { useContext } from "react"
import {
  SearchContext,
  SearchDispatchContext,
  type SearchContextValue,
  type SearchDispatchContextValue,
} from "./SearchContext"

// Custom hook to use the search context
export const useSearchState = (): SearchContextValue => {
  const context = useContext(SearchContext)
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
