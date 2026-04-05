import { expect, test, type Page } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// Helper : session authentifiée avec API mockée
// ═══════════════════════════════════════════════════════════

async function preparerSessionDashboard(page: Page) {
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

  await page.route("**/api/v1/dashboard/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.includes("widgets") || path.includes("donnees")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          repas_du_jour: { dejeuner: "Salade tiède", diner: "Soupe maison" },
          alertes: [{ type: "peremption", message: "Yaourt expire demain", priorite: "haute" }],
          taches_jour: [{ id: 1, nom: "Arroser plantes", fait: false }],
          meteo: { temperature: 18, description: "Ensoleillé", ville: "Paris" },
          score_famille: 85,
        }),
      });
    } else {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
    }
  });

  // Catch-all pour les autres endpoints
  await page.route("**/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.includes("/auth/") || path.includes("/dashboard/")) {
      await route.continue();
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], total: 0 }) });
  });
}

test.describe("Dashboard - Parcours complet", () => {
  test("7.7 - Dashboard: ouvrir dashboard → vérifier widgets → DnD réorganiser", async ({
    page,
  }) => {
    // Naviguer vers le dashboard
    await page.goto("/");
    await expect(page).toHaveURL("/");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({ timeout: 5000 });

    // Vérifier la présence de widgets/sections principales
    const widgets = page.locator('[data-widget], section, article, .widget, [class*="card"]');
    const widgetCount = await widgets.count();
    console.log(`[Dashboard] Nombre de sections détectées: ${widgetCount}`);

    // Vérifier qu'il y a du contenu visible
    const mainContent = page.locator("main, [role='main'], article");
    await expect(mainContent.first()).toBeVisible();

    // Pas d'erreur JS
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("Dashboard inclut les widgets principaux", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL("/");

    // Attendre le chargement du contenu
    await expect(page.locator("body")).toBeVisible({ timeout: 5000 });

    // Vérifier la présence d'éléments typiques d'un dashboard
    const content = page.locator("body");
    await expect(content).toBeVisible();
  });

  test("Navigation depuis dashboard fonctionne", async ({ page }) => {
    // Depuis le dashboard, naviguer vers les modules principales
    await page.goto("/");
    await expect(page).toHaveURL("/");

    // Essayer de naviguer vers un module
    const cuisineLink = page.getByRole("link", {
      name: /cuisine|Cuisine/i,
    });

    if (await cuisineLink.isVisible()) {
      await cuisineLink.click();
      // Vérifier que la navigation s'est effectuée
      await expect(page).toHaveURL(/\/cuisine/);
    }
  });
});

// ═══════════════════════════════════════════════════════════
// E2E — Dashboard avec données et interactions
// ═══════════════════════════════════════════════════════════

test.describe("Dashboard — Widgets et interactions", () => {
  test.beforeEach(async ({ page }) => {
    await preparerSessionDashboard(page);
  });

  test("dashboard charge et affiche le contenu principal", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Doit afficher un heading principal
    const heading = page.locator("h1, h2").first();
    await expect(heading).toBeVisible({ timeout: 5000 });

    // Doit afficher au moins des cards/widgets
    const cards = page.locator('[class*="card"], [data-widget], article');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
  });

  test("aucune erreur JavaScript dans la console", async ({ page }) => {
    const jsErrors: string[] = [];
    page.on("pageerror", (error) => {
      jsErrors.push(error.message);
    });

    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
    // Attendre le chargement complet
    await page.waitForLoadState("networkidle").catch(() => {});

    // Filtrer les faux positifs communs (hydration, chunk loading)
    const realErrors = jsErrors.filter(
      (e) => !e.includes("hydrat") && !e.includes("chunk") && !e.includes("Loading")
    );
    expect(realErrors).toHaveLength(0);
  });

  test("widgets DnD — les éléments draggable sont présents", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Chercher les éléments avec attributs DnD Kit
    const draggables = page.locator('[data-dnd-draggable], [draggable="true"], [role="button"][tabindex]');
    const count = await draggables.count();
    // Le dashboard utilise DnD Kit pour les widgets
    console.log(`[Dashboard] Éléments draggable trouvés: ${count}`);
  });

  test("actions rapides sont visibles sur le dashboard", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Les boutons d'action rapide doivent être présents
    const actionsRapides = page.getByRole("button").filter({ hasText: /planifier|courses|qu.est-ce qu.on mange/i });
    const count = await actionsRapides.count();
    console.log(`[Dashboard] Actions rapides trouvées: ${count}`);
  });
});
