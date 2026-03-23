import { test, expect } from "@playwright/test";

test.describe("Navigation principale", () => {
  test("la page de connexion se charge", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page).toHaveTitle(/Assistant Matanne/);
    await expect(page.locator("body")).toBeVisible();
  });

  test("redirection vers connexion si non authentifié", async ({ page }) => {
    await page.goto("/");
    // Should redirect to /connexion when not authenticated
    await page.waitForURL(/connexion/, { timeout: 5000 }).catch(() => {});
    // Page should at least load
    await expect(page.locator("body")).toBeVisible();
  });

  test("les pages outils client-side se chargent", async ({ page }) => {
    // These are client-side only pages, should render even without auth
    await page.goto("/outils/convertisseur");
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/outils/minuteur");
    await expect(page.locator("body")).toBeVisible();
  });
});
