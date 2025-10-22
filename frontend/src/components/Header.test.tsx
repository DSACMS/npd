import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import Header from "./Header"

describe("Header", () => {
  it("renders header content", async () => {
    render(<Header />)
    expect(screen.getByText("National Provider Directory")).toBeInTheDocument()
  })
})
