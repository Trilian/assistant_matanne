import { expect, test } from "@playwright/test";

test.describe("Visual regression", () => {
  test("connexion page should match baseline", async ({ page }) => {
    await page.goto("/connexion");
    await page.setViewportSize({ width: 1366, height: 768 });
    await expect(page).toHaveScreenshot("connexion-desktop.png", {
      fullPage: true,
      animations: "disabled",
    });
  });

  test("connexion mobile should match baseline", async ({ page }) => {
    await page.goto("/connexion");
    await page.setViewportSize({ width: 393, height: 852 });
    await expect(page).toHaveScreenshot("connexion-mobile.png", {
      fullPage: true,
      animations: "disabled",
    });
  });
});
