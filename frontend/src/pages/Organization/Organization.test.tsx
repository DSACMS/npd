import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it } from "vitest"
import {
  DEFAULT_FRONTEND_SETTINGS,
  mockGlobalFetch,
} from "../../../tests/mockGlobalFetch"
import { render } from "../../../tests/render"
import { Organization } from "./Organization"

describe("Organization", () => {
  it("does not render content when feature flag is unset", async () => {
    render(<Organization />)
    await waitFor(() => {
      expect(screen.queryByText("Provider group")).toBeInTheDocument()
      expect(screen.queryByText("Details go here.")).toBeNull()
    })
  })

  describe("with ORGANIZATION_LOOKUP_DETAILS feature flag", () => {
    beforeEach(() => {
      // update /api/frontend_settings mocked response
      mockGlobalFetch([
        [
          "^/api/frontend_settings$",
          {
            ...DEFAULT_FRONTEND_SETTINGS,
            feature_flags: {
              ORGANIZATION_LOOKUP_DETAILS: true,
            },
          },
        ],
      ])
    })

    it("shows detailed content", async () => {
      render(<Organization />)
      await waitFor(() => {
        expect(screen.queryByText("Provider group")).toBeInTheDocument()
        expect(screen.queryByText("Details go here.")).toBeInTheDocument()
      })
    })
  })
})
