import { expect, test } from "@playwright/test"

test.describe("authentication", () => {
  test("local dev default account can sign in", async ({ page }) => {
    // act: click on "Sign in" link in header
    await page.goto("")
    await page.getByRole("link", { name: "Sign in" }).click()

    // assert: we're looking at the login screen
    await expect(page).toHaveURL("/accounts/login/")
    await expect(page.locator("#login-form")).toBeVisible()
    await expect(page.locator("form legend")).toContainText("Sign in")

    // act: sign in
    await page.locator("#username").fill("developer@cms.hhs.gov")
    await page.locator("#password-sign-in").fill("password123")
    await page.getByRole("button", { name: "Sign in" }).click()

    // assert: redirection after successful sign-in sends user to the landing
    // page with updated header
    await expect(page).toHaveURL("/")
    await expect(page.locator("form#authentication-form")).toContainText(
      "Sign out",
    )
    await expect(page.locator("h1")).toContainText(
      "National Provider Directory",
    )
  })
})
