import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { SluggedHeading } from "./SluggedHeading"

describe("SluggedHeading", () => {
  it("returns a React component", async () => {
    const Component = SluggedHeading("h1")
    expect(Component).toBeTypeOf("function")
  })

  describe("returned component", () => {
    it("renders a header with correct attributes", () => {
      const Component = SluggedHeading("h3")
      render(<Component>Participating in the test</Component>)

      const element = screen.getByText("Participating in the test", {
        selector: "h3",
      })
      expect(element.ariaLevel).toEqual("4")
      expect(element.role).toEqual("heading")
      expect(element.id).toEqual("participating-in-the-test")
    })
  })
})
