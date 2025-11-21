import { describe, expect, it } from "vitest"
import { apiUrl } from "./api"

describe("apiUrl", () => {
  it("returns an api URL", () => {
    const url = apiUrl("/my/path")
    expect(url).toEqual("http://localhost:8000/my/path")
  })

  it("replaces template placeholders", () => {
    const url = apiUrl("/my/path/:placeholder", { placeholder: "THING" })
    expect(url).toEqual("http://localhost:8000/my/path/THING")
  })
})
