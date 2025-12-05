import { Outlet } from "react-router"
import { Footer } from "../components/Footer"
import { Header } from "../components/Header"
import { LoadingIndicator } from "../components/LoadingIndicator"
import { useFrontendSettings } from "../hooks/useFrontendSettings"

// A react-router compatible page wrapper.
export const Layout = () => {
  const { loading } = useFrontendSettings()

  // do not render a page until frontend settings have finished loading
  return (
    <>
      <Header />
      {loading ? <LoadingIndicator /> : <Outlet />}
      <Footer />
    </>
  )
}
