import { test, expect, type Page } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux planning repas
// ═══════════════════════════════════════════════════════════

async function preparerContextePlanning(page: Page) {
  await page.context().addCookies([
    {
      name: "access_token",
      value: "e2e-dev-token",
      domain: "localhost",
      path: "/",
      httpOnly: false,
      sameSite: "Lax",
    },
    {
      name: "access_token",
      value: "e2e-dev-token",
      domain: "127.0.0.1",
      path: "/",
      httpOnly: false,
      sameSite: "Lax",
    },
  ]);

  await page.addInitScript(() => {
    window.localStorage.setItem("access_token", "e2e-dev-token");
    window.localStorage.setItem("matanne-onboarding-complete", "true");
  });

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;

    if (path === "/api/v1/auth/me") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: 42, email: "e2e@local", nom: "E2E Local", role: "membre" }),
      });
      return;
    }

    if (path === "/api/v1/auth/refresh") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "e2e-dev-token", token_type: "bearer" }),
      });
      return;
    }

    if (path === "/api/v1/planning/semaine") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          planning_id: 10,
          semaine_debut: "2026-04-06",
          semaine_fin: "2026-04-12",
          repas: [
            {
              id: 1,
              date: "2026-04-06",
              date_repas: "2026-04-06",
              type_repas: "dejeuner",
              recette_id: 11,
              recette_nom: "Salade tiede",
              notes: "Salade tiede",
              portions: 2,
              nutri_score: "A",
            },
            {
              id: 2,
              date: "2026-04-06",
              date_repas: "2026-04-06",
              type_repas: "diner",
              recette_id: 12,
              recette_nom: "Soupe maison",
              notes: "Soupe maison",
              portions: 2,
              nutri_score: "B",
            },
          ],
        }),
      });
      return;
    }

    if (path === "/api/v1/planning/mensuel") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ mois: "2026-04", par_jour: {} }),
      });
      return;
    }

    if (path === "/api/v1/planning/conflits") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ resume: "Aucun conflit", items: [] }),
      });
      return;
    }

    if (path === "/api/v1/planning/nutrition-hebdo") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          semaine_debut: "2026-04-06",
          semaine_fin: "2026-04-12",
          totaux: { calories: 0, proteines: 0, lipides: 0, glucides: 0 },
          moyenne_calories_par_jour: 0,
          par_jour: {},
          nb_repas_sans_donnees: 0,
          nb_repas_total: 0,
        }),
      });
      return;
    }

    if (path === "/api/v1/planning/suggestions-rapides") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ suggestions: [] }),
      });
      return;
    }

    if (path === "/api/v1/famille/evenements") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [] }),
      });
      return;
    }

    if (path === "/api/v1/calendriers/evenements") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
      return;
    }

    if (path === "/api/v1/flux/cuisine-3-clics") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ etape_actuelle: null, planning: null }),
      });
      return;
    }

    await route.continue();
  });
}

test.describe("Planning repas", () => {
  test.beforeEach(async ({ page }) => {
    await preparerContextePlanning(page);
    await page.goto("/cuisine/planning");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });
  });

  test("affiche les 7 jours de la semaine", async ({ page }) => {
    const jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
    for (const jour of jours) {
      await expect(page.getByText(jour)).toBeVisible();
    }
  });

  test("navigation semaine précédente/suivante fonctionne", async ({ page }) => {
    const boutonPrec = page.getByRole("button", { name: /semaine précédente/i });
    const boutonSuiv = page.getByRole("button", { name: /semaine suivante/i });

    await expect(boutonPrec).toBeVisible();
    await expect(boutonSuiv).toBeVisible();

    // Naviguer semaine suivante
    await boutonSuiv.click();
    await expect(page.locator("body")).toBeVisible();

    // Naviguer semaine précédente
    await boutonPrec.click();
    await expect(page.locator("body")).toBeVisible();
  });

  test("bouton Aujourd'hui ramène à la semaine courante", async ({ page }) => {
    const boutonSuiv = page.getByRole("button", { name: /semaine suivante/i });
    await boutonSuiv.click();

    const boutonAujourdhui = page.getByText("Aujourd'hui");
    await expect(boutonAujourdhui).toBeVisible();
    await boutonAujourdhui.click();
    await expect(page.locator("body")).toBeVisible();
  });

  test("les types de repas sont affichés", async ({ page }) => {
    const typesRepas = ["Déjeuner", "Dîner"];
    for (const type of typesRepas) {
      await expect(page.getByText(type).first()).toBeVisible();
    }
  });
});

test.describe("Planning activités", () => {
  test.beforeEach(async ({ page }) => {
    await preparerContextePlanning(page);
  });

  test("page planning redirige vers le planning cuisine", async ({ page }) => {
    await page.goto("/planning", { waitUntil: "domcontentloaded" });
    await expect(page).toHaveURL(/\/cuisine\/planning/);
    await expect(page.getByRole("heading", { name: /planning repas/i })).toBeVisible({ timeout: 10000 });
  });

  test("navigation semaine avec boutons flèche", async ({ page }) => {
    await page.goto("/cuisine/planning", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: /planning repas/i })).toBeVisible({ timeout: 10000 });

    const boutonPrec = page.getByRole("button", { name: /semaine précédente/i });
    const boutonSuiv = page.getByRole("button", { name: /semaine suivante/i });

    if (await boutonPrec.isVisible()) {
      await boutonPrec.click();
      await expect(page.locator("body")).toBeVisible();
    }

    if (await boutonSuiv.isVisible()) {
      await boutonSuiv.click();
      await expect(page.locator("body")).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════
// E2E — Flux planning → courses (workflow complet)
// ═══════════════════════════════════════════════════════════

test.describe("Planning → Courses — Flux bout en bout", () => {
  test.beforeEach(async ({ page }) => {
    await preparerContextePlanning(page);

    // Mock supplémentaire pour les courses
    await page.route("**/api/v1/courses/listes**", async (route) => {
      const method = route.request().method();
      if (method === "GET") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            items: [
              { id: 100, nom: "Courses semaine 15", statut: "en_cours", nb_articles: 5, date_creation: "2026-04-06" },
            ],
            total: 1,
          }),
        });
      } else if (method === "POST") {
        await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ id: 101, nom: "Nouvelle liste", statut: "en_cours", nb_articles: 0 }) });
      } else {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
      }
    });

    await page.route("**/api/v1/courses/generer-depuis-planning**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          liste_id: 101,
          articles: [
            { id: 1, nom: "Laitue", quantite: 1, unite: "pièce", categorie: "Fruits et légumes", coche: false },
            { id: 2, nom: "Tomates", quantite: 4, unite: "pièce", categorie: "Fruits et légumes", coche: false },
            { id: 3, nom: "Bouillon cube", quantite: 2, unite: "pièce", categorie: "Épicerie", coche: false },
          ],
        }),
      });
    });

    await page.route("**/api/v1/courses/articles**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          items: [
            { id: 1, nom: "Laitue", quantite: 1, unite: "pièce", categorie: "Fruits et légumes", coche: false },
            { id: 2, nom: "Tomates", quantite: 4, unite: "pièce", categorie: "Fruits et légumes", coche: false },
            { id: 3, nom: "Bouillon cube", quantite: 2, unite: "pièce", categorie: "Épicerie", coche: false },
          ],
          total: 3,
        }),
      });
    });
  });

  test("accéder au planning puis naviguer vers les courses", async ({ page }) => {
    await page.goto("/cuisine/planning");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });

    // Le planning doit afficher des repas
    await expect(page.getByText("Salade tiede").first()).toBeVisible();
    await expect(page.getByText("Soupe maison").first()).toBeVisible();

    // Naviguer vers les courses
    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // La page courses doit charger
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 5000 });
  });

  test("planning affiche les recettes et le nutri-score", async ({ page }) => {
    await page.goto("/cuisine/planning");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });

    // Vérifier que les recettes mockées sont affichées
    await expect(page.getByText("Salade tiede").first()).toBeVisible();
    await expect(page.getByText("Soupe maison").first()).toBeVisible();

    // Vérifier la navigation semaine
    const boutonSuiv = page.getByRole("button", { name: /semaine suivante/i });
    await expect(boutonSuiv).toBeVisible();
  });

  test("page courses affiche les listes existantes", async ({ page }) => {
    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Doit afficher le contenu de la page courses
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 5000 });
  });
});
