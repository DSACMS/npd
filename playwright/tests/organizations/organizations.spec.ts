import { expect, test } from "@playwright/test"

import fhir_organization from "../../../frontend/tests/fixtures/fhir_organization.json"
import fhir_organizations from "../../../frontend/tests/fixtures/fhir_organizations.json"

test.describe("Organizations", () => {
  test("visit an Organization page", async ({ page }) => {
    // mock the API using the existing test fixture from frontend/
    await page.route("*/**/fhir/Organization/12345/", async (route) => {
      const json = fhir_organization
      await route.fulfill({ json })
    })

    await page.goto("/organizations/12345")

    await expect(page).toHaveURL("/organizations/12345")

    await expect(page.locator("div[role='heading']")).toContainText(
      "Acme Healthcare System",
    )
  })

  test("visit the Organizations listing page", async ({ page }) => {
    await page.route(
      new RegExp(".*/fhir/Organization/\\?.*"),
      async (route) => {
        const json = fhir_organizations
        await route.fulfill({ json })
      },
    )

    await page.goto("/organizations")

    await expect(page).toHaveURL("/organizations")

    await expect(page.locator("div[role='heading']")).toContainText(
      "All Organizations",
    )

    await expect(page.getByText("NPI: 1679576367")).toBeInViewport()
  })
})
