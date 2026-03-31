import { expect, test } from "@playwright/test";

test.describe("Maison flow complet", () => {
  test("parcours hub -> travaux -> jardin -> finances -> contrats", async ({ page }) => {
    await page.goto("/maison");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Maison");

    await page.goto("/maison/travaux");
    await expect(page).toHaveURL(/\/maison\/travaux/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/maison/jardin");
    await expect(page).toHaveURL(/\/maison\/jardin/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/maison/finances");
    await expect(page).toHaveURL(/\/maison\/finances/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/maison/contrats");
    await expect(page).toHaveURL(/\/maison\/contrats/);
    await expect(page.locator("body")).toBeVisible();
  });
});
