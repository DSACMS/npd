import { expect, test } from "@playwright/test"
import { ORGANIZATION } from "../constants"

let organization = ORGANIZATION

// load a known organization record from the API before running tests
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
      name: "AAA Test Org",
      npi: "1234567893",
    }),
  )
})

test.describe("Organization search", () => {
  test("search for an Organization by NPI", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("1234567893")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by exact name", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("AAA Test Org")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by partial name", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })
})

test.describe("Organization show", () => {
  test("visit an Organization page", async ({ page }) => {
    await page.goto("/organizations/search")
    
    await page.getByRole("textbox", { name: "Name or NPI" }).fill(organization.name)
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: organization.name }).click()

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

test.describe("sort Organizations", () => {
  test("sort dropdown is visible after search", async ({ page }) => {
    await page.goto("/organizations/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("Name (A-Z)")
  })

  test("sort search results by name descending", async ({ page }) => {
    await page.goto("/organizations/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toContainText("Name (A-Z)")

    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()

    await expect(page).toHaveURL(/query=Test/)
    await expect(page).toHaveURL(/sort=name-desc/)
    await expect(sortButton).toContainText("Name (Z-A)")
  })
})

test("search by NPI excludes organizations with matching other_id", async ({ page }) => {
  await page.goto("/organizations/search")
  
  await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567893")
  await page.getByRole("button", { name: "Search" }).click()
  
  await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  await expect(page.getByRole("link", { name: "BBB Other ID Org" })).not.toBeVisible()
})
