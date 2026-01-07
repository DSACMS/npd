import { expect, test } from "@playwright/test"

let organization: { npi: string; id: string; name: string } = {
  npi: "UNSET",
  id: "UNSET",
  name: "UNSET",
}

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

test.describe("Organization listing", () => {
  test("visit the Organizations listing page", async ({ page }) => {
    await page.goto("/organizations")

    await expect(page).toHaveURL("/organizations")

    await expect(page.locator("div[role='heading']")).toContainText(
      "All Organizations",
    )

    await expect(page.getByText(`NPI: ${organization?.npi}`)).toBeVisible()
  })

  test("paging through Organizations", async ({ page }) => {
    await page.goto("/organizations")

    await expect(page).toHaveURL("/organizations")

    // assert
    await expect(page.getByRole("caption")).toContainText(
      "Showing 1 - 10 of 26",
    )
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(10)

    // act
    await page.getByLabel("Next Page").first().click()

    // assert
    await expect(page).toHaveURL("/organizations?page=2")
    await expect(page.getByRole("caption")).toContainText(
      "Showing 11 - 20 of 26",
    )
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(10)

    // act
    await page.getByLabel("Next Page").first().click()

    // assert
    await expect(page).toHaveURL("/organizations?page=3")
    await expect(page.locator("span[role='caption']")).toContainText(
      "Showing 21 - 26 of 26",
    )
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(6)
  })
})

test.describe("Organization search", () => {
  test("search for an Organization by NPI", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Search Organizations")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI, EIN" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI, EIN" })
      .fill("1234567893")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by exact name", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Search Organizations")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI, EIN" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI, EIN" })
      .fill("AAA Test Org")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by partial name", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Search Organizations")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI, EIN" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI, EIN" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })
})

test.describe("Organization show", () => {
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

test.describe("sort Organizations", () => {
  test("sort dropdown is visible on listing page", async ({ page }) => {
    await page.goto("/organizations")
    
    await expect(page.locator(".ds-c-dropdown__button")).toBeVisible()
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Name (A-Z)")
  })

  test("sort listing results by name descending", async ({ page }) => {
    await page.goto("/organizations")

    await page.locator(".ds-c-dropdown__button").click()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()

    await expect(page).toHaveURL(/sort=name-desc/)
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Name (Z-A)")
  })

  test("sort persists through pagination", async ({ page }) => {
    await page.goto("/organizations")

    await page.locator(".ds-c-dropdown__button").click()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()
    await expect(page).toHaveURL(/sort=name-desc/)

    await page.getByLabel("Next Page").first().click()

    await expect(page).toHaveURL(/page=2/)
    await expect(page).toHaveURL(/sort=name-desc/)
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Name (Z-A)")
  })

  test("sort search results", async ({ page }) => {
    await page.goto("/organizations/search")

    await page.getByRole("textbox", { name: "Name or Identifier (NPI, EIN" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    await page.locator(".ds-c-dropdown__button").click()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()

    await expect(page).toHaveURL(/query=Test/)
    await expect(page).toHaveURL(/sort=name-desc/)
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Name (Z-A)")
  })
})
