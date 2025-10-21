import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Landing } from "./Landing"

describe("Landing", () => {
  it("renders landing page content", async () => {
    render(<Landing />)

    // header
    expect(
      screen.getByText("National Provider Directory", { selector: "h1" }),
    ).toBeInTheDocument()

    // body
    expect(screen.getByText("LIMITED-RELEASE BETA")).toBeInTheDocument()

    // footer
    expect(
      screen.getByText("7500 Security Boulevard, Baltimore, MD 21244"),
    ).toBeInTheDocument()
  })
})
