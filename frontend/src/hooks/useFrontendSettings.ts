import { useContext } from "react"
import { FrontendSettingsContext } from "../state/FrontendSettingsProvider"

export const useFrontendSettings = () => {
  const context = useContext(FrontendSettingsContext)
  if (!context) {
    throw new Error(
      "useFrontendSettings must be used within a FrontendSettingsProvider",
    )
  }
  return context
}

export const useFeatureFlags = () => {
  const {
    settings: { feature_flags },
  } = useFrontendSettings()
  return feature_flags
}

export const useAuthenticatedUser = () => {
  const {
    settings: { user },
  } = useFrontendSettings()
  return user
}
