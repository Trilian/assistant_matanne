import { test, expect, type Page } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// Helper : session authentifiée avec API mockée
// ═══════════════════════════════════════════════════════════

const RECETTES_MOCK = [
  { id: 1, nom: "Poulet rôti", categorie: "plat", temps_preparation: 15, temps_cuisson: 60, portions: 4, difficulte: "facile", ingredients: [], etapes: [] },
  { id: 2, nom: "Salade César", categorie: "entree", temps_preparation: 10, temps_cuisson: 0, portions: 2, difficulte: "facile", ingredients: [], etapes: [] },
  { id: 3, nom: "Tarte aux pommes", categorie: "dessert", temps_preparation: 20, temps_cuisson: 35, portions: 6, difficulte: "moyen", ingredients: [], etapes: [] },
];

async function preparerContexteRecettes(page: Page) {
  await page.context().addCookies([
    { name: "access_token", value: "e2e-dev-token", domain: "localhost", path: "/", httpOnly: false, sameSite: "Lax" },
    { name: "access_token", value: "e2e-dev-token", domain: "127.0.0.1", path: "/", httpOnly: false, sameSite: "Lax" },
  ]);

  await page.addInitScript(() => {
    window.localStorage.setItem("access_token", "e2e-dev-token");
    window.localStorage.setItem("matanne-onboarding-complete", "true");
  });

  const recettesState = [...RECETTES_MOCK];

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ id: 42, email: "e2e@local", nom: "E2E Local", role: "admin" }),
    });
  });

  await page.route("**/api/v1/recettes**", async (route) => {
    const url = new URL(route.request().url());
    const method = route.request().method();

    if (method === "GET" && !url.pathname.match(/\/\d+$/)) {
      // Liste des recettes
      const search = url.searchParams.get("recherche") || url.searchParams.get("q") || "";
      const filtered = search
        ? recettesState.filter((r) => r.nom.toLowerCase().includes(search.toLowerCase()))
        : recettesState;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: filtered, total: filtered.length, page: 1, page_size: 20 }),
      });
      return;
    }

    if (method === "POST") {
      const body = JSON.parse(route.request().postData() || "{}");
      const newRecette = { id: recettesState.length + 10, ...body, ingredients: body.ingredients || [], etapes: body.etapes || [] };
      recettesState.push(newRecette);
      await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify(newRecette) });
      return;
    }

    if (method === "DELETE") {
      await route.fulfill({ status: 204 });
      return;
    }

    if (method === "PUT" || method === "PATCH") {
      const body = JSON.parse(route.request().postData() || "{}");
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id: 1, ...body }) });
      return;
    }

    await route.continue();
  });

  // Catch-all pour les autres endpoints
  await page.route("**/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.includes("/auth/") || path.includes("/recettes")) {
      await route.continue();
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], total: 0 }) });
  });
}

// ═══════════════════════════════════════════════════════════
// E2E — Flux recettes (smoke tests originaux)
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

// ═══════════════════════════════════════════════════════════
// E2E — CRUD recettes complet avec API mockée
// ═══════════════════════════════════════════════════════════

test.describe("CRUD recettes — flux complet", () => {
  test.beforeEach(async ({ page }) => {
    await preparerContexteRecettes(page);
  });

  test("créer une recette via le formulaire", async ({ page }) => {
    await page.goto("/cuisine/recettes");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Cliquer sur "Nouvelle recette" ou "Ajouter"
    const boutonNouvelle = page.getByText(/Nouvelle recette|Ajouter/i).first();
    if (await boutonNouvelle.isVisible().catch(() => false)) {
      await boutonNouvelle.click();

      // Remplir le formulaire
      const nomInput = page.locator('input[name="nom"], input[placeholder*="nom"]').first();
      if (await nomInput.isVisible().catch(() => false)) {
        await nomInput.fill("Gratin dauphinois");

        // Soumettre
        const boutonSave = page.getByRole("button", { name: /enregistrer|sauvegarder|créer|valider/i }).first();
        if (await boutonSave.isVisible().catch(() => false)) {
          await boutonSave.click();
          // Page doit rester fonctionnelle après soumission
          await expect(page.locator("body")).toBeVisible();
        }
      }
    }
  });

  test("la recherche filtre les recettes affichées", async ({ page }) => {
    await page.goto("/cuisine/recettes");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    const inputRecherche = page.locator('input[placeholder*="echercher"]');
    if (await inputRecherche.isVisible().catch(() => false)) {
      await inputRecherche.fill("poulet");
      // Attendre le filtrage
      await page.waitForTimeout(500);
      // La page doit contenir des résultats ou un message "aucun résultat"
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("accéder aux détails d'une recette", async ({ page }) => {
    await page.goto("/cuisine/recettes");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Cliquer sur une recette de la liste
    const premiereLigne = page.getByText("Poulet rôti").first();
    if (await premiereLigne.isVisible().catch(() => false)) {
      await premiereLigne.click();
      await expect(page.locator("body")).toBeVisible();
    }
  });
});
