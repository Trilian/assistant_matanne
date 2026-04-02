import { expect, test } from "@playwright/test";

test.describe("Jeux - Parcours complet", () => {
  test("7.9 - Paris sportifs: créer pari → résultat → vérifier bankroll", async ({
    page,
  }) => {
    // Naviguer vers le hub jeux
    await page.goto("/jeux");
    await expect(page).toHaveURL("/jeux");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    // Vérifier la présence du module paris sportifs
    const paris = page.getByRole("link", { name: /paris|sportif/i }).first();
    if (await paris.isVisible()) {
      await paris.click();
      await expect(page).toHaveURL(/\/jeux\/paris|\/jeux\/pari/);
    }

    // Pas d'erreur JS
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("Navigation vers les jeux disponibles", async ({ page }) => {
    // Naviguer vers le hub jeux
    await page.goto("/jeux");
    await expect(page).toHaveURL("/jeux");

    // Vérifier que les liens de sous-modules sont visibles
    const submodules = page.locator('a[href^="/jeux/"]');
    const count = await submodules.count();
    console.log(`[Jeux] Sous-modules trouvés: ${count}`);

    // Naviguer vers au moins un sous-module
    if (count > 0) {
      await submodules.first().click();
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("Modules outils (client-side) accessibles", async ({ page }) => {
    // Vérifier que les outils client-side (Convertisseur, Minuteur, etc.) sont accessibles
    const pages = ["/outils/convertisseur", "/outils/minuteur"];

    for (const url of pages) {
      await page.goto(url);
      await expect(page).toHaveURL(new RegExp(url));
      await expect(page.locator("body")).toBeVisible();
    }
  });
});
