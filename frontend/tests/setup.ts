import * as matchers from "@testing-library/jest-dom/matchers"
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, beforeEach, expect, vi } from "vitest"
import { mockGlobalFetch } from "./mockGlobalFetch"

// ensure translations are supported
import "../src/i18n"

expect.extend(matchers)
beforeEach(() => {
  mockGlobalFetch()
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks() // Clear mocks after each test
})
