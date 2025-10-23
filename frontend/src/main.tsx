import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { BrowserRouter, Route, Routes } from "react-router"
import { Landing } from "./pages/Landing.tsx"

import "@cmsgov/design-system/css/core-theme.css"
import "@cmsgov/design-system/css/index.css"
import "@cmsgov/design-system/dist/fonts/opensans-bold-webfont.woff2"
import "@cmsgov/design-system/dist/fonts/opensans-regular-webfont.woff2"

// raw USWDS styles
import "@uswds/uswds/css/uswds.css"

// USWDS javascript behaviors
import "@uswds/uswds"

import "./i18n.ts"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/developers" element={<Landing />} />
        <Route path="/providers" element={<Landing />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
