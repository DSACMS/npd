import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Route, Routes } from "react-router"

import "@cmsgov/design-system/dist/fonts/opensans-bold-webfont.woff2"
import "@cmsgov/design-system/dist/fonts/opensans-regular-webfont.woff2"
import "./index.css"

// USWDS javascript behaviors
import "@uswds/uswds"

import "./i18n.ts"

import { AuthenticatedRoute } from "./components/AuthenticatedRoute.tsx"
import { Developers } from "./pages/Developers"
import { Landing } from "./pages/Landing"
import { Layout } from "./pages/Layout"
import { Login } from "./pages/Login.tsx"
import { FrontendSettingsProvider } from "./state/FrontendSettingsProvider.tsx"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <FrontendSettingsProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/accounts/login/" element={<Login />} />
            <Route element={<AuthenticatedRoute />}>
              <Route index element={<Landing />} />
              <Route path="/developers" element={<Developers />} />
            </Route>
          </Route>
        </Routes>
      </FrontendSettingsProvider>
    </BrowserRouter>
  </StrictMode>,
)
