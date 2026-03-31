import { expect, test } from "@playwright/test";

test.describe("Cuisine flow complet", () => {
  test("parcours hub -> recettes -> courses -> inventaire", async ({ page }) => {
    await page.goto("/cuisine");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Cuisine");

    await page.getByRole("link", { name: /Recettes/i }).first().click();
    await expect(page).toHaveURL(/\/cuisine\/recettes/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/cuisine/courses");
    await expect(page).toHaveURL(/\/cuisine\/courses/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/cuisine/inventaire");
    await expect(page).toHaveURL(/\/cuisine\/inventaire/);
    await expect(page.locator("body")).toBeVisible();
  });
});
