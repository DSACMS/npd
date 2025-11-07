import { Navigate, Outlet } from "react-router"
import { useFrontendSettings } from "../hooks/useFrontendSettings"

export const FeatureFlagRoute = ({ name }: { name: string }) => {
  const {
    settings: { feature_flags },
    loading,
  } = useFrontendSettings()

  if (loading) return null

  if (feature_flags?.[name]) {
    return <Outlet />
  }
  console.warn("route is not available")
  return <Navigate to="/" replace />
}
