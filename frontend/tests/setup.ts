import * as matchers from "@testing-library/jest-dom/matchers"
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, expect } from "vitest"

// ensure translations are supported
import "../src/i18n"

expect.extend(matchers)

afterEach(() => {
  cleanup()
})
