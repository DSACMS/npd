import { useContext } from "react"
import { SearchContext, type SearchContextValue } from "./SearchContext"

// Custom hook to use the search context
export const useSearch = (): SearchContextValue => {
  const context = useContext(SearchContext)
  if (context === undefined) {
    throw new Error("useSearch must be used within a SearchProvider")
  }
  return context
}
