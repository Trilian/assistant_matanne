import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Inter-modules (Planning -> Courses -> Inventaire)
// ═══════════════════════════════════════════════════════════

async function configurerContexteInterModules(page: import("@playwright/test").Page) {
  let prochainIdListe = 2;
  const listes = [
    {
      id: 1,
      nom: "Courses semaine",
      date_creation: "2026-03-23T08:00:00Z",
      est_terminee: false,
      articles: [],
      nombre_articles: 2,
      nombre_coche: 0,
    },
  ];
  const detailsListes = new Map<number, {
    id: number;
    nom: string;
    date_creation: string;
    est_terminee: boolean;
    nombre_articles: number;
    nombre_coche: number;
    articles: Array<{
      id: number;
      nom: string;
      quantite: number;
      categorie: string;
      est_coche: boolean;
    }>;
  }>();

  detailsListes.set(1, {
    id: 1,
    nom: "Courses semaine",
    date_creation: "2026-03-23T08:00:00Z",
    est_terminee: false,
    nombre_articles: 2,
    nombre_coche: 0,
    articles: [
      { id: 1, nom: "Pommes", quantite: 6, categorie: "Fruits", est_coche: false },
      { id: 2, nom: "Lait", quantite: 2, categorie: "Laitier", est_coche: false },
    ],
  });

  await page.context().addCookies([
    {
      name: "access_token",
      value: "e2e-dev-token",
      url: "http://localhost:3000",
      httpOnly: false,
      sameSite: "Lax",
    },
  ]);

  await page.addInitScript(() => {
    window.localStorage.setItem("access_token", "e2e-dev-token");
    window.localStorage.setItem("matanne-onboarding-complete", "true");
  });

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        id: 42,
        email: "e2e@local",
        nom: "E2E Local",
        role: "membre",
      }),
    });
  });

  await page.route("**/api/v1/planning/semaine*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        planning_id: 10,
        semaine_debut: "2026-03-23",
        semaine_fin: "2026-03-29",
        repas: [],
      }),
    });
  });

  await page.route("**/api/v1/planning/conflits*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        date_debut: "2026-03-23",
        conflits: [],
        total: 0,
      }),
    });
  });

  await page.route("**/api/v1/planning/nutrition-hebdo*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        semaine_debut: "2026-03-23",
        semaine_fin: "2026-03-29",
        totaux: { calories: 0, proteines: 0, lipides: 0, glucides: 0 },
        moyenne_calories_par_jour: 0,
        par_jour: {},
        nb_repas_sans_donnees: 0,
        nb_repas_total: 0,
      }),
    });
  });

  await page.route("**/api/v1/courses/recurrents-suggeres", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ suggestions: [], total: 0 }),
    });
  });

  await page.route("**/api/v1/courses/*/bio-local", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        liste_id: 1,
        mois: "2026-03",
        suggestions: [],
        nb_en_saison: 0,
      }),
    });
  });

  await page.route("**/api/v1/courses", async (route) => {
    const requete = route.request();

    if (requete.method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(listes),
      });
      return;
    }

    if (requete.method() === "POST") {
      const donnees = requete.postDataJSON() as { nom?: string };
      const nouvelleListe = {
        id: prochainIdListe++,
        nom: donnees.nom?.trim() || "Nouvelle liste",
        date_creation: "2026-03-23T08:05:00Z",
        est_terminee: false,
        articles: [],
        nombre_articles: 0,
        nombre_coche: 0,
      };
      listes.push(nouvelleListe);
      detailsListes.set(nouvelleListe.id, nouvelleListe);

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(nouvelleListe),
      });
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/v1/courses/*", async (route) => {
    const requete = route.request();
    const url = new URL(requete.url());
    const segments = url.pathname.split("/");
    const identifiant = Number(segments[segments.length - 1]);

    if (requete.method() === "GET" && Number.isFinite(identifiant)) {
      const detail = detailsListes.get(identifiant) ?? {
        id: identifiant,
        nom: `Liste ${identifiant}`,
        date_creation: "2026-03-23T08:10:00Z",
        est_terminee: false,
        nombre_articles: 0,
        nombre_coche: 0,
        articles: [],
      };

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(detail),
      });
      return;
    }

    await route.fallback();
  });

  await page.route("**/api/v1/inventaire/alertes", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([]),
    });
  });

  await page.route("**/api/v1/inventaire**", async (route) => {
    const requete = route.request();
    if (requete.method() !== "GET") {
      await route.fallback();
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 1,
          nom: "Lait",
          quantite: 2,
          unite: "bouteilles",
          categorie: "Laitier",
          emplacement: "Frigo",
        },
      ]),
    });
  });
}

test.describe("Inter-modules cuisine", () => {
  test("navigation planning -> courses -> inventaire", async ({ page }) => {
    await configurerContexteInterModules(page);

    await page.goto("/cuisine/planning");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });
    await expect(page.getByRole("heading", { name: /planning repas/i })).toBeVisible();

    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const hasCoursesContext =
      (await page.locator('input[placeholder*="Nouvelle liste"]').isVisible().catch(() => false)) ||
      (await page.locator("text=Courses").first().isVisible().catch(() => false));
    expect(hasCoursesContext).toBeTruthy();

    await page.goto("/cuisine/inventaire");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const hasInventaireContext =
      (await page.locator("text=Inventaire").first().isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="Rechercher"]').isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="rechercher"]').isVisible().catch(() => false));
    expect(hasInventaireContext).toBeTruthy();
  });

  test("création de liste courses puis consultation inventaire", async ({ page }) => {
    await configurerContexteInterModules(page);

    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const inputNom = page.locator('input[placeholder*="Nouvelle liste"]');
    const nomListe = `Flow-${Date.now()}`;

    await expect(inputNom).toBeVisible();
    await inputNom.fill(nomListe);

    const boutonCreer = page.getByRole("button", { name: /créer la liste/i });
    await expect(boutonCreer).toBeEnabled();

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/api/v1/courses") &&
          response.request().method() === "POST" &&
          response.status() === 200
      ),
      boutonCreer.click(),
    ]);

    await expect(page.getByRole("button", { name: new RegExp(nomListe, "i") }).first()).toBeVisible();

    await page.goto("/cuisine/inventaire");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const hasInventaireContext =
      (await page.locator("text=Inventaire").first().isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="Rechercher"]').isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="rechercher"]').isVisible().catch(() => false));
    expect(hasInventaireContext).toBeTruthy();
  });
});
