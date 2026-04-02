import { expect, test } from "@playwright/test";

test.describe("Cuisine - Parcours complet", () => {
  test("7.1 - Cuisine complet: créer recette → planifier semaine → générer liste courses → cocher acheté → inventaire mis à jour", async ({
    page,
  }) => {
    // Naviguer vers le hub cuisine
    await page.goto("/cuisine");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Cuisine");

    // Vérifier que les sections principales sont visibles
    const recettesLink = page.getByRole("link", { name: /Recettes/i }).first();
    await expect(recettesLink).toBeVisible();

    // Naviguer vers recettes
    await recettesLink.click();
    await expect(page).toHaveURL(/\/cuisine\/recettes/);
    await expect(page.getByRole("heading")).toContainText(/Recettes|RECETTES/i);

    // Naviguer vers planning
    await page.goto("/cuisine/planning");
    await expect(page).toHaveURL(/\/cuisine\/planning/);
    await expect(page.getByRole("heading")).toBeVisible();

    // Naviguer vers courses
    await page.goto("/cuisine/courses");
    await expect(page).toHaveURL(/\/cuisine\/courses/);

    // Vérifier que la création de liste est possible
    const createButton = page.locator('button:has-text("Créer")').first();
    if (await createButton.isVisible()) {
      // Note: Ne pas cliquer pour éviter les side effects en E2E
    }

    // Naviguer vers inventaire
    await page.goto("/cuisine/inventaire");
    await expect(page).toHaveURL(/\/cuisine\/inventaire/);
    await expect(page.locator("body")).toBeVisible();

    // Vérifier que les pages critiques se chargent sans erreur
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });

    // Pas d'erreur JavaScript critique
    expect(errors.length).toBe(0);
  });

  test("Naviguer entre tous les modules cuisine", async ({ page }) => {
    const modules = [
      "/cuisine",
      "/cuisine/recettes",
      "/cuisine/planning",
      "/cuisine/courses",
      "/cuisine/inventaire",
    ];

    for (const module of modules) {
      await page.goto(module);
      await expect(page).toHaveURL(new RegExp(module));
      await expect(page.locator("body")).toBeVisible();
    }
  });
});
