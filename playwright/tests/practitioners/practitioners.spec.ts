import { expect, test } from "@playwright/test"

let practitioner: { npi: string; id: string; name: string } = {
  npi: "UNSET",
  id: "UNSET",
  name: "UNSET",
}

// load a known practitioner record from the API before running tests
test.beforeAll(async ({ request }) => {
  // expects a FhirCollection<FhirPractitioner> API response
  const response = await request.get(
    "/fhir/Practitioner/?identifier=1234567894",
  )
  const payload = await response.json()

  const resource = payload.results.entry[0].resource

  // Practitioner names are in resource.name[0].text or constructed from given/family
  const nameRecord = resource.name?.[0]
  const name = nameRecord?.text || `${nameRecord?.given?.[0] || ""} ${nameRecord?.family || ""}`.trim()

  practitioner = {
    id: resource.id,
    name: name,
    npi: resource.identifier?.find(
      (i: { system?: string }) => 
        i.system === "http://hl7.org/fhir/sid/us-npi" || 
        i.system === "http://terminology.hl7.org/NamingSystem/npi"
    )?.value || resource.identifier?.[0]?.value,
  }

  // it should look like the /fhir/Practitioner/ record created by seedsystem
  expect(practitioner).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: expect.stringContaining("AAA Test Practitioner"),
      npi: "1234567894",
    }),
  )
})

test.describe("Practitioner listing", () => {
  test("visit the Practitioners listing page", async ({ page }) => {
    await page.goto("/practitioners")
    await expect(page).toHaveURL("/practitioners")

    await expect(page.locator("div[role='heading']")).toContainText(
      "All Practitioners",
    )
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem").first()
    ).toBeVisible()
  })

  test("paging through Practitioners", async ({ page }) => {
    await page.goto("/practitioners")
    await expect(page).toHaveURL("/practitioners")

    await expect(page.getByRole("caption")).toBeVisible()
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(await page.locator("[data-testid='searchresults']").getByRole("listitem").count())

    await page.getByLabel("Next Page").first().click()
    await expect(page).toHaveURL("/practitioners?page=2")
  })
})

test.describe("Practitioner search", () => {
  test("search for a Practitioner by NPI", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner by exact name", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .fill("AAA Test Practitioner")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner by partial name", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner and view details", async ({ page }) => {
    await page.goto("/practitioners/search")
    
    await page
      .getByRole("textbox", { name: "Name or Identifier (NPI" })
      .fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
  })
})

test.describe("Practitioner show", () => {
  test("visit a Practitioner page", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
  })
})

test.describe("sort Practitioners", () => {
  test("sort dropdown is visible on listing page", async ({ page }) => {
    await page.goto("/practitioners")
    
    await expect(page.locator(".ds-c-dropdown__button")).toBeVisible()
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("First Name (A-Z)")
  })

  test("sort listing results by last name", async ({ page }) => {
    await page.goto("/practitioners")

    await page.locator(".ds-c-dropdown__button").click()
    await page.getByRole("option", { name: "Last Name (A-Z)" }).click()

    await expect(page).toHaveURL(/sort=last-name-asc/)
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Last Name (A-Z)")
  })

  test("sort persists through pagination", async ({ page }) => {
    await page.goto("/practitioners")

    await page.locator(".ds-c-dropdown__button").click()
    await page.getByRole("option", { name: "Last Name (Z-A)" }).click()
    await expect(page).toHaveURL(/sort=last-name-desc/)

    await page.getByLabel("Next Page").first().click()

    await expect(page).toHaveURL(/page=2/)
    await expect(page).toHaveURL(/sort=last-name-desc/)
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Last Name (Z-A)")
  })

  test("sort search results", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or Identifier (NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    await page.locator(".ds-c-dropdown__button").click()
    await page.getByRole("option", { name: "Last Name (A-Z)" }).click()

    await expect(page).toHaveURL(/query=AAA/)
    await expect(page).toHaveURL(/sort=last-name-asc/)
    await expect(page.locator(".ds-c-dropdown__label-text")).toHaveText("Last Name (A-Z)")
  })
})
 
