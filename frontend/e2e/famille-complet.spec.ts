import { expect, test } from "@playwright/test";

test.describe("Famille flow complet", () => {
  test("parcours hub -> jules -> activites -> budget -> routines", async ({ page }) => {
    await page.goto("/famille");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Famille");

    await page.goto("/famille/jules");
    await expect(page).toHaveURL(/\/famille\/jules/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/famille/activites");
    await expect(page).toHaveURL(/\/famille\/activites/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/famille/budget");
    await expect(page).toHaveURL(/\/famille\/budget/);
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/famille/routines");
    await expect(page).toHaveURL(/\/famille\/routines/);
    await expect(page.locator("body")).toBeVisible();
  });
});
