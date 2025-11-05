import * as matchers from "@testing-library/jest-dom/matchers"
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, expect, vi } from "vitest"

// ensure translations are supported
import "../src/i18n"

expect.extend(matchers)

// Mock the global fetch function
global.fetch = vi.fn<typeof global.fetch>((input: RequestInfo | URL) => {
  if (input === "/frontend_settings") {
    return Promise.resolve({
      ok: true,
      json: () =>
        Promise.resolve({
          authentication_required: false,
          user: { is_anonymous: false, username: "testuser" },
        }),
    } as Response)
  }

  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  } as Response)
})

afterEach(() => {
  cleanup()
  vi.clearAllMocks() // Clear mocks after each test
})
