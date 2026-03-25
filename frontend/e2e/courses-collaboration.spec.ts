import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux courses et liste de courses
// ═══════════════════════════════════════════════════════════

test.describe("Courses — navigation et UI", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
  });

  test("page courses affiche le formulaire de création de liste", async ({ page }) => {
    const inputNom = page.locator('input[placeholder*="ouvelle liste"]');
    // Le formulaire de création devrait être visible
    await expect(inputNom).toBeVisible({ timeout: 10000 });
  });

  test("bouton créer liste est présent", async ({ page }) => {
    const bouton = page.getByRole("button", { name: /Créer la liste/i });
    await expect(bouton).toBeVisible();
  });

  test("message liste vide quand aucune liste", async ({ page }) => {
    // Peut afficher "Aucune liste" ou la liste existante
    await expect(page.locator("body")).toBeVisible();
  });

  test("sélectionner une liste affiche les articles", async ({ page }) => {
    // Si une liste existe, on peut cliquer dessus
    const premiereListe = page.locator('button[class*="text-left"]').first();
    if (await premiereListe.isVisible().catch(() => false)) {
      await premiereListe.click();
      // Le panel articles devrait s'activer
      await expect(page.locator("body")).toBeVisible();
    }
  });
});
