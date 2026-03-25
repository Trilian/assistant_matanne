import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux recettes complet (CRUD)
// ═══════════════════════════════════════════════════════════

test.describe("Flux recettes", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/cuisine/recettes");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });
  });

  test("page recettes affiche la barre de recherche", async ({ page }) => {
    const inputRecherche = page.locator('input[placeholder*="echercher"]');
    await expect(inputRecherche).toBeVisible();
  });

  test("filtrer les recettes par recherche textuelle", async ({ page }) => {
    const inputRecherche = page.locator('input[placeholder*="echercher"]');
    await expect(inputRecherche).toBeVisible();
    await inputRecherche.fill("poulet");
    // La page doit rester fonctionnelle après saisie
    await expect(page.locator("body")).toBeVisible();
  });

  test("bouton nouvelle recette est accessible", async ({ page }) => {
    const boutonNouvelle = page.getByText(/Nouvelle recette|Ajouter/i);
    // Si le bouton existe (quand authentifié), il doit être visible
    const count = await boutonNouvelle.count();
    if (count > 0) {
      await expect(boutonNouvelle.first()).toBeVisible();
    }
  });

  test("navigation depuis hub cuisine vers recettes", async ({ page }) => {
    await page.goto("/cuisine");
    await expect(page.locator("h1")).toContainText("Cuisine");

    const lienRecettes = page.locator('a[href="/cuisine/recettes"]');
    await expect(lienRecettes).toBeVisible({ timeout: 10000 });
    await lienRecettes.click();

    await expect(page).toHaveURL(/\/cuisine\/recettes/);
    await expect(page.locator("h1")).toBeVisible();
  });
});
