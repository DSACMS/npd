import { expect, test } from "@playwright/test"

let organization: { npi: string; id: string; name: string } = {
  npi: "UNSET",
  id: "UNSET",
  name: "UNSET",
}

// load an organization record from the API before running tests
test.beforeAll(async ({ request }) => {
  // expects a FhirCollection<FhirOrganization> API response
  const response = await request.get(
    "/fhir/Organization/?identifier=1234567893",
  )
  const payload = await response.json()

  const resource = payload.results.entry[0].resource

  organization = {
    id: resource.id,
    name: resource.name,
    npi: resource.identifier[0].value,
  }

  // it should look like the /fhir/Organization/ record created by seedsystem
  expect(organization).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: "Test Org",
      npi: "1234567893",
    }),
  )
})

test.describe("Organizations", () => {
  test("visit the Organizations listing page", async ({ page }) => {
    await page.goto("/organizations")

    await expect(page).toHaveURL("/organizations")

    await expect(page.locator("div[role='heading']")).toContainText(
      "All Organizations",
    )

    await expect(page.getByText(`NPI: ${organization?.npi}`)).toBeVisible()
  })

  test("visit an Organization page", async ({ page }) => {
    // visit listing page
    await page.goto("/organizations")

    // pick known organization
    await page.getByText(organization.name).click()

    // should be on the single organization show page
    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    await expect(page.locator("div[role='heading']")).toContainText(
      organization.name,
    )

    const banner = page.locator("section.banner")
    await expect(banner.getByText("Provider group")).toBeVisible()
    await expect(banner.getByText(organization.name)).toBeVisible()
    await expect(banner.getByText(`NPI: ${organization.npi}`)).toBeVisible()
  })
})
