import { expect, test } from "@playwright/test"

import fhir_practitioner from "../../../frontend/tests/fixtures/fhir_practitioner.json"

test.describe("Practitioners", () => {
  test.use({ storageState: "tests/.auth/user.json" })

  test("visit a practitioner page", async ({ page }) => {
    // mock the API using the existing test fixture from frontend/
    await page.route(
      "*/**/fhir/Practitioner/73768136-3d4e-453c-a761-1a13962a42eb/",
      async (route) => {
        const json = fhir_practitioner
        await route.fulfill({ json })
      },
    )

    await page.goto("/practitioners/73768136-3d4e-453c-a761-1a13962a42eb")

    await expect(page).toHaveURL(
      "/practitioners/73768136-3d4e-453c-a761-1a13962a42eb",
    )

    await expect(page.locator("h1[role='heading']")).toContainText(
      "DR. KIRK AADALEN",
    )
  })
})
