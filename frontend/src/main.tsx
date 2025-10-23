import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Route, Routes } from "react-router"

import "@cmsgov/design-system/css/core-theme.css"
import "@cmsgov/design-system/css/index.css"
import "@cmsgov/design-system/dist/fonts/opensans-bold-webfont.woff2"
import "@cmsgov/design-system/dist/fonts/opensans-regular-webfont.woff2"

// raw USWDS styles
import "@uswds/uswds/css/uswds.css"

// USWDS javascript behaviors
import "@uswds/uswds"

import "./i18n.ts"

import { Developers } from "./pages/Developers"
import { Landing } from "./pages/Landing"
import { Layout } from "./pages/Layout"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="/developers" element={<Developers />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
