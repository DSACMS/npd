import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Developers } from "./Developers"

describe("Developers", () => {
  it("renders developer page headings", async () => {
    render(<Developers />)
    expect(
      screen.getByText("Documentation", { selector: "[role=heading]" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("For developers", { selector: "span" }),
    ).toBeInTheDocument()
  })

  it("renders developer page markdown content", () => {
    render(<Developers />)
    expect(
      screen.getByText(
        "This is a brief overview of the National Provider Directory project.",
        {
          selector: "p",
        },
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Participating in the beta", {
        selector: "h3",
      }),
    ).toBeInTheDocument()
  })
})
