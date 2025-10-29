import { Outlet } from "react-router"
import { Footer } from "../components/Footer"
import { Header } from "../components/Header"

// A react-router compatible page wrapper.
export const Layout = () => {
  return (
    <>
      <Header />
      <Outlet />
      <Footer />
    </>
  )
}
