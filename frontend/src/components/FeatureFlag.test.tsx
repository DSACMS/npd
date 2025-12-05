import { screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it } from "vitest"
import {
  DEFAULT_FRONTEND_SETTINGS,
  mockGlobalFetch,
} from "../../tests/mockGlobalFetch"
import { render } from "../../tests/render"
import { FeatureFlag } from "./FeatureFlag"

describe("FeatureFlag", () => {
  it("does not render content when feature flag is not set", async () => {
    render(<FeatureFlag name="SOMETHING">Some content</FeatureFlag>)
    await waitFor(() => {
      expect(screen.queryByText("Some content")).toBeNull()
    })
  })

  describe("inverse", () => {
    it("renders content when feature flag is not set and inverse is used", async () => {
      render(
        <FeatureFlag name="SOMETHING" inverse>
          Some content
        </FeatureFlag>,
      )
      await waitFor(() => {
        expect(screen.queryByText("Some content")).toBeInTheDocument()
      })
    })
  })

  describe("with SOMETHING set", () => {
    beforeEach(() => {
      mockGlobalFetch([
        [
          "^/api/frontend_settings$",
          {
            ...DEFAULT_FRONTEND_SETTINGS,
            feature_flags: {
              SOMETHING: true,
            },
          },
        ],
      ])
    })

    it("renders content", async () => {
      render(<FeatureFlag name="SOMETHING">Some content</FeatureFlag>)
      await waitFor(() => {
        expect(screen.queryByText("Some content")).toBeInTheDocument()
      })
    })

    it("does not render inverse content", async () => {
      render(
        <FeatureFlag inverse name="SOMETHING">
          Some content
        </FeatureFlag>,
      )
      await waitFor(() => {
        expect(screen.queryByText("Some content")).toBeNull()
      })
    })
  })
})
