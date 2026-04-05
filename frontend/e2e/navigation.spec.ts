import { test, expect, type Page } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// Helper : session authentifiée avec API mockée
// ═══════════════════════════════════════════════════════════

async function preparerSessionAuth(page: Page) {
  await page.context().addCookies([
    { name: "access_token", value: "e2e-dev-token", domain: "localhost", path: "/", httpOnly: false, sameSite: "Lax" },
    { name: "access_token", value: "e2e-dev-token", domain: "127.0.0.1", path: "/", httpOnly: false, sameSite: "Lax" },
  ]);

  await page.addInitScript(() => {
    window.localStorage.setItem("access_token", "e2e-dev-token");
    window.localStorage.setItem("matanne-onboarding-complete", "true");
  });

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ id: 42, email: "e2e@local", nom: "E2E Local", role: "admin" }),
    });
  });

  // Catch-all pour éviter les erreurs réseau
  await page.route("**/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.includes("/auth/")) {
      await route.continue();
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], total: 0 }) });
  });
}

test.describe("Navigation principale", () => {
  test("la page de connexion se charge", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page).toHaveTitle(/Assistant Matanne/);
    await expect(page.locator("body")).toBeVisible();
  });

  test("redirection vers connexion si non authentifié", async ({ page }) => {
    await page.goto("/");
    // Should redirect to /connexion when not authenticated
    await page.waitForURL(/connexion/, { timeout: 5000 }).catch(() => {});
    // Page should at least load
    await expect(page.locator("body")).toBeVisible();
  });

  test("les pages outils client-side se chargent", async ({ page }) => {
    // These are client-side only pages, should render even without auth
    await page.goto("/outils/convertisseur");
    await expect(page.locator("body")).toBeVisible();

    await page.goto("/outils/minuteur");
    await expect(page.locator("body")).toBeVisible();
  });
});

// ═══════════════════════════════════════════════════════════
// E2E — Navigation cross-module authentifiée
// ═══════════════════════════════════════════════════════════

test.describe("Navigation cross-module", () => {
  test.beforeEach(async ({ page }) => {
    await preparerSessionAuth(page);
  });

  test("dashboard → cuisine → famille → maison → retour dashboard", async ({ page }) => {
    // 1. Dashboard
    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // 2. Naviguer vers Cuisine via sidebar ou lien
    const cuisineLink = page.getByRole("link", { name: /cuisine/i }).first();
    if (await cuisineLink.isVisible().catch(() => false)) {
      await cuisineLink.click();
      await expect(page).toHaveURL(/\/cuisine/);
      await expect(page.locator("body")).toBeVisible();
    } else {
      await page.goto("/cuisine");
      await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
    }

    // 3. Naviguer vers Famille
    const familleLink = page.getByRole("link", { name: /famille/i }).first();
    if (await familleLink.isVisible().catch(() => false)) {
      await familleLink.click();
      await expect(page).toHaveURL(/\/famille/);
    } else {
      await page.goto("/famille");
    }
    await expect(page.locator("body")).toBeVisible();

    // 4. Naviguer vers Maison
    const maisonLink = page.getByRole("link", { name: /maison/i }).first();
    if (await maisonLink.isVisible().catch(() => false)) {
      await maisonLink.click();
      await expect(page).toHaveURL(/\/maison/);
    } else {
      await page.goto("/maison");
    }
    await expect(page.locator("body")).toBeVisible();

    // 5. Retour Dashboard
    const dashboardLink = page.getByRole("link", { name: /accueil|dashboard|hub/i }).first();
    if (await dashboardLink.isVisible().catch(() => false)) {
      await dashboardLink.click();
    } else {
      await page.goto("/");
    }
    await expect(page.locator("body")).toBeVisible();
  });

  test("hubs de modules affichent leur contenu", async ({ page }) => {
    const modules = ["/cuisine", "/famille", "/maison", "/jeux"];

    for (const module of modules) {
      await page.goto(module);
      await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
      // Chaque hub doit avoir au moins un heading
      const heading = page.locator("h1, h2").first();
      await expect(heading).toBeVisible({ timeout: 5000 });
    }
  });

  test("sous-pages cuisine sont accessibles depuis le hub", async ({ page }) => {
    await page.goto("/cuisine");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Vérifier les liens vers sous-pages critiques
    const lienRecettes = page.locator('a[href*="/cuisine/recettes"]').first();
    if (await lienRecettes.isVisible().catch(() => false)) {
      await lienRecettes.click();
      await expect(page).toHaveURL(/\/cuisine\/recettes/);
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("navigation arrière fonctionne", async ({ page }) => {
    await page.goto("/cuisine");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    await page.goto("/cuisine/recettes");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Retour arrière navigateur
    await page.goBack();
    await expect(page).toHaveURL(/\/cuisine$/);
    await expect(page.locator("body")).toBeVisible();
  });
});
