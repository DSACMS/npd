import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Footer } from "./Footer"

describe("Footer", () => {
  it("renders footer content", async () => {
    render(<Footer />)
    expect(screen.getByText("CMS & HHS")).toBeInTheDocument()
    expect(
      screen.getByText("7500 Security Boulevard, Baltimore, MD 21244"),
    ).toBeInTheDocument()
  })
})
