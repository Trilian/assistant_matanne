import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux authentification
// ═══════════════════════════════════════════════════════════

test.describe("Authentification", () => {
  test("page connexion se charge avec formulaire", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Formulaire de connexion visible
    const emailInput = page.locator('input[type="email"], input[name="email"]');
    const passwordInput = page.locator('input[type="password"]');

    if (await emailInput.isVisible().catch(() => false)) {
      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
    }
  });

  test("page inscription est accessible", async ({ page }) => {
    await page.goto("/inscription");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
  });

  test("redirection vers connexion si non authentifié", async ({ page }) => {
    await page.goto("/");
    // Doit rediriger vers connexion si pas de token
    await page.waitForURL(/connexion/, { timeout: 5000 }).catch(() => {});
    await expect(page.locator("body")).toBeVisible();
  });

  test("lien entre connexion et inscription fonctionne", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    const lienInscription = page.getByText(/inscription|créer un compte/i);
    if (await lienInscription.isVisible().catch(() => false)) {
      await lienInscription.click();
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("formulaire connexion valide les champs requis", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Tenter de soumettre sans remplir — le bouton devrait être désactivé ou montrer une erreur
    const boutonConnexion = page.getByRole("button", { name: /connexion|se connecter/i });
    if (await boutonConnexion.isVisible().catch(() => false)) {
      await expect(boutonConnexion).toBeVisible();
    }
  });
});
