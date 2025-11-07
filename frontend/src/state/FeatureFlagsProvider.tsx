import { createContext, useContext, useEffect, useState } from "react"
import { apiUrl } from "./api"

export type FeatureFlagState = {
  flags: Record<string, boolean>
  loading: boolean
  error?: string | null
  refetch: () => void
}

// Create the context
const FeatureFlagContext = createContext<FeatureFlagState>({
  flags: {},
  loading: true,
  refetch: () => {},
})

// Custom hook to use the context
// eslint-disable-next-line react-refresh/only-export-components
export const useFeatureFlags = () => {
  const context = useContext(FeatureFlagContext)
  if (!context) {
    throw new Error(
      "useFeatureFlags must be used within a FeatureFlagsProvider",
    )
  }
  return context
}

// Provider component
export const FeatureFlagsProvider = ({ children }: React.PropsWithChildren) => {
  const [settings, setSettings] = useState<FrontendSettings>({})
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>()

  const fetchFlags = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(apiUrl("/frontend_settings"))
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setSettings(data as unknown as FrontendSettings)
    } catch (err: unknown) {
      setError((err as Error).message)
      console.error("Failed to fetch frontend settings:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFlags()
  }, [])

  const value = {
    settings,
    loading,
    error,
    refetch: () => {
      // Allow manual refetch if needed
      setLoading(true)
      setError(null)
      fetchFlags()
    },
  }

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  )
}
