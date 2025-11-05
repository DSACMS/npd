import { screen, waitFor } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../tests/render"
import { Header } from "./Header"

describe("Header", () => {
  it("renders header content", async () => {
    render(<Header />)
    await waitFor(() => {
      expect(
        screen.getByText("National Provider Directory"),
      ).toBeInTheDocument()
    })
  })

  it("shows Sign out button", async () => {
    render(<Header />)
    await waitFor(() => {
      expect(
        screen.getByText("Sign out", { selector: "button" }),
      ).toBeInTheDocument()
    })
  })
})
