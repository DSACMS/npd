import { Navigate, Outlet } from "react-router"
import { useFrontendSettings } from "../state/FrontendSettingsProvider"

export const AuthenticatedRoute = () => {
  const { settings, loading } = useFrontendSettings()

  if (loading) return null

  if (settings.require_authentication && settings.user?.is_anonymous) {
    console.warn("authentication is required", { user: settings.user })
    return <Navigate to="/accounts/login/" replace />
  }
  return <Outlet />
}
