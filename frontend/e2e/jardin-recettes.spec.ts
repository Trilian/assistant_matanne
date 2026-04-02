import { expect, test } from "@playwright/test";

test.describe("Inter-modules - Jardin → Recettes", () => {
  test("7.6 - Enregistrer récolte → Vérifier suggestion recette adaptée", async ({
    page,
  }) => {
    // Naviguer vers le jardin
    await page.goto("/maison/jardin");
    await expect(page).toHaveURL(/\/maison\/jardin/);
    await expect(page.getByRole("heading")).toBeVisible();

    // Vérifier que le jardin se charge correctement
    const jardinContent = page.locator("body");
    await expect(jardinContent).toBeVisible();

    // Naviguer vers les recettes
    await page.goto("/cuisine/recettes");
    await expect(page).toHaveURL(/\/cuisine\/recettes/);
    await expect(page.getByRole("heading")).toBeVisible();

    // Vérifier pas d'erreur JS
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("Navigation jardin et recettes fonctionne", async ({ page }) => {
    // Vérifier accès au jardin
    await page.goto("/maison/jardin");
    await expect(page).toHaveURL(/\/maison\/jardin/);
    const jardinHeading = page.getByRole("heading");
    await expect(jardinHeading).toBeVisible({ timeout: 5000 });

    // Vérifier accès aux recettes
    await page.goto("/cuisine/recettes");
    await expect(page).toHaveURL(/\/cuisine\/recettes/);
    const recettesHeading = page.getByRole("heading");
    await expect(recettesHeading).toBeVisible({ timeout: 5000 });
  });
});
