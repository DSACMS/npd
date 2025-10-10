import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import Header from "./components/Header.tsx"
import UrlList from "./components/UrlList.tsx"

import "@cmsgov/design-system/css/core-theme.css"
import "@cmsgov/design-system/css/index.css"
import "@cmsgov/design-system/dist/fonts/opensans-bold-webfont.woff2"
import "@cmsgov/design-system/dist/fonts/opensans-regular-webfont.woff2"

import "@uswds/uswds/css/uswds.css"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Header />
    <UrlList />
  </StrictMode>,
)
