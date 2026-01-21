import { expect, test } from "@playwright/test"

const FHIR_RESOURCES = [
  "Endpoint",
  "Location",
  "Organization",
  "Practitioner",
  "PractitionerRole",
  "metadata",
] as const

test.describe("Swagger UI", () => {
  test("loads successfully", async ({ page }) => {
    await page.goto("/fhir/docs/")

    await expect(page.locator("#swagger-ui")).toBeVisible()
    await expect(page.locator(".info .title")).toContainText("NPD FHIR API")
  })

  test("displays all FHIR resource tags", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    for (const resource of FHIR_RESOURCES) {
      const tag = page.locator(`h3.opblock-tag[data-tag="${resource}"]`)
      await expect(tag).toBeVisible()
    }
  })
})

test.describe("Swagger UI - Organization", () => {
  test("execute GET /fhir/Organization/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Organization-Organization_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })

  test("execute GET /fhir/Organization/{id}/", async ({ page }) => {
    // First get a valid organization ID
    const orgResponse = await page.request.get("/fhir/Organization/?identifier=1234567893")
    const orgData = await orgResponse.json()
    const orgId = orgData.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Organization-Organization_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()

    await operation.locator("tr[data-param-name='id'] input").fill(orgId)
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })
})

test.describe("Swagger UI - Practitioner", () => {
  test("execute GET /fhir/Practitioner/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Practitioner-Practitioner_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })

  test("execute GET /fhir/Practitioner/{id}/", async ({ page }) => {
    // First get a valid practitioner ID
    const response = await page.request.get("/fhir/Practitioner/?identifier=1234567894")
    const data = await response.json()
    const practitionerId = data.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Practitioner-Practitioner_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()

    await operation.locator("tr[data-param-name='id'] input").fill(practitionerId)
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })
})

test.describe("Swagger UI - Location", () => {
  test("execute GET /fhir/Location/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Location-Location_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })

//   test("execute GET /fhir/Location/{id}/", async ({ page }) => {
//     we dont have any locations currently in test database
//   })
})

test.describe("Swagger UI - Endpoint", () => {
  test("execute GET /fhir/Endpoint/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Endpoint-Endpoint_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })

  test("execute GET /fhir/Endpoint/{id}/", async ({ page }) => {
    // First get a valid endpoint ID
    const response = await page.request.get("/fhir/Endpoint/")
    const data = await response.json()

    const endpointId = data.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Endpoint-Endpoint_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()

    await operation.locator("tr[data-param-name='id'] input").fill(endpointId)
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })
})

test.describe("Swagger UI - PractitionerRole", () => {
  test("execute GET /fhir/PractitionerRole/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-PractitionerRole-PractitionerRole_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })

//   test("execute GET /fhir/PractitionerRole/{id}/", async ({ page }) => {
//     // we dont have any PractitionerRoles currently in test database
//   })
})

test.describe("Swagger UI - metadata", () => {
  test("execute GET /fhir/metadata/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-metadata-metadata_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200", { timeout: 10000 })
  })
})