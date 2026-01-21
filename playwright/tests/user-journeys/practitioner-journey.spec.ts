import { expect, test } from "@playwright/test"

let practitioner: { npi: string; id: string; name: string } = {
  npi: "UNSET",
  id: "UNSET",
  name: "UNSET",
}

// load a known practitioner record from the API before running tests
test.beforeAll(async ({ request }) => {
  const response = await request.get(
    "/fhir/Practitioner/?identifier=NPI|1234567894",
  )
  const payload = await response.json()
  const resource = payload.results.entry[0].resource

  const nameRecord = resource.name?.[0]
  const name = nameRecord?.text || 
    `${nameRecord?.given?.[0] || ""} ${nameRecord?.family || ""}`.trim()

  practitioner = {
    id: resource.id,
    name: name,
    npi: resource.identifier?.find(
      (i: { system?: string }) => 
        i.system === "http://hl7.org/fhir/sid/us-npi" || 
        i.system === "http://terminology.hl7.org/NamingSystem/npi"
    )?.value || resource.identifier?.[0]?.value,
  }

  expect(practitioner).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: expect.stringContaining("AAA Test Practitioner"),
      npi: "1234567894",
    }),
  )
})

test.describe("Practitioner Journey", () => {
  test("landing -> search hub -> practitioner search -> detail view", async ({ page }) => {
    // first, start at landing page
    await page.goto("/")
    await expect(page).toHaveURL("/")

    // then, navigate to search hub
    await page.getByRole("link", { name: /search/i }).first().click()
    await expect(page).toHaveURL("/search")

    // then, select Practitioner search
    await page.getByRole("link", { name: /practitioner/i }).click()
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    // then, perform search by NPI
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()

    // then, confirm search results appear
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()

    // then, click on practitioner to view details
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    // then, confirm detail page content
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
  })

  test("landing -> practitioner detail", async ({ page }) => {
    await page.goto("/")

    await page.getByRole("link", { name: /search/i }).first().click()
    await page.getByRole("link", { name: /practitioner/i }).click()

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA Test Practitioner")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
  })

  test("practitioner journey with partial name search", async ({ page }) => {
    await page.goto("/")

    await page.getByRole("link", { name: /search/i }).first().click()
    await page.getByRole("link", { name: /practitioner/i }).click()

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
  })

  test("practitioner journey with sorting functionality", async ({ page }) => {
    await page.goto("/")

    await page.getByRole("link", { name: /search/i }).first().click()
    await page.getByRole("link", { name: /practitioner/i }).click()

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("First Name (A-Z)")

    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Last Name (A-Z)" }).click()

    await expect(page).toHaveURL(/sort=last-name-asc/)
    await expect(sortButton).toContainText("Last Name (A-Z)")

    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
  })
})
