import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Landing } from "./Landing"

describe("Landing", () => {
  it("renders landing page content", async () => {
    render(<Landing />)
    expect(
      screen.getByText("National Provider Directory", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(screen.getByText("LIMITED-RELEASE BETA")).toBeInTheDocument()
  })
})
