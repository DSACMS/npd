import { createContext, useEffect, useState } from "react"
import { apiUrl } from "./api"

export type FrontendSettingsState = {
  settings: FrontendSettings
  loading: boolean
  error?: string | null
  refetch: () => void
}

// Create the context
// eslint-disable-next-line react-refresh/only-export-components
export const FrontendSettingsContext = createContext<FrontendSettingsState>({
  settings: {},
  loading: true,
  refetch: () => {},
})

// Provider component
export const FrontendSettingsProvider = ({
  children,
}: React.PropsWithChildren) => {
  const [settings, setSettings] = useState<FrontendSettings>({})
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>()

  const fetchSettings = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(apiUrl("/api/frontend_settings"))
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
    fetchSettings()
  }, [])

  const value = {
    settings,
    loading,
    error,
    refetch: () => {
      // Allow manual refetch if needed
      setLoading(true)
      setError(null)
      fetchSettings()
    },
  }

  return (
    <FrontendSettingsContext.Provider value={value}>
      {children}
    </FrontendSettingsContext.Provider>
  )
}
