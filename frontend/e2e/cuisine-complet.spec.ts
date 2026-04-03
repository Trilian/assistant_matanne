import { expect, test, type Page } from "@playwright/test";

async function configurerContexteCuisineComplet(page: Page) {
  let prochainRecetteId = 101;
  let prochainListeId = 401;
  let prochainArticleId = 801;

  const recettes: Array<{
    id: number;
    nom: string;
    description: string;
    instructions: string;
    ingredients: Array<{ nom: string; quantite: number; unite: string }>;
    categorie: string;
    difficulte: string;
    temps_preparation: number;
    temps_cuisson: number;
    portions: number;
  }> = [];
  const recettesPlanifiees = new Set<number>();
  const listes: Array<{
    id: number;
    nom: string;
    etat: "brouillon" | "confirmee" | "terminee";
    date_creation: string;
    est_terminee: boolean;
    nombre_articles: number;
    nombre_coche: number;
  }> = [];
  const detailsListes = new Map<number, {
    id: number;
    nom: string;
    etat: "brouillon" | "confirmee" | "terminee";
    date_creation: string;
    est_terminee: boolean;
    nombre_articles: number;
    nombre_coche: number;
    articles: Array<{
      id: number;
      nom: string;
      quantite: number;
      unite: string;
      categorie: string;
      est_coche: boolean;
    }>;
  }>();
  const inventaire: Array<{
    id: number;
    nom: string;
    categorie: string;
    quantite: number;
    unite: string;
    emplacement: string;
    est_bas: boolean;
    est_expire: boolean;
  }> = [];

  const recetteParId = (id: number) => recettes.find((recette) => recette.id === id) ?? null;
  const listeParId = (id: number) => detailsListes.get(id) ?? null;

  function synchroniserResumeListe(listeId: number) {
    const detail = listeParId(listeId);
    const resume = listes.find((liste) => liste.id === listeId);
    if (!detail || !resume) return;
    resume.nom = detail.nom;
    resume.etat = detail.etat;
    resume.est_terminee = detail.est_terminee;
    resume.nombre_articles = detail.articles.length;
    resume.nombre_coche = detail.articles.filter((article) => article.est_coche).length;
    detail.nombre_articles = resume.nombre_articles;
    detail.nombre_coche = resume.nombre_coche;
  }

  function construirePlanning() {
    const idsPlanifies = Array.from(recettesPlanifiees);
    return {
      planning_id: 10,
      semaine_debut: "2026-03-23",
      semaine_fin: "2026-03-29",
      repas: idsPlanifies.map((id, index) => {
        const recette = recetteParId(id)!;
        return {
          id: 600 + index,
          date: "2026-03-23",
          date_repas: "2026-03-23",
          type_repas: "diner",
          recette_id: recette.id,
          recette_nom: recette.nom,
          notes: recette.nom,
          portions: recette.portions,
          nutri_score: "A",
        };
      }),
    };
  }

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
    const method = request.method();

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

    if (path === "/api/v1/recettes" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          items: recettes,
          total: recettes.length,
          page: 1,
          pages_totales: 1,
        }),
      });
      return;
    }

    if (path === "/api/v1/recettes" && method === "POST") {
      const payload = request.postDataJSON() as {
        nom: string;
        description?: string;
        instructions?: string;
        ingredients?: Array<{ nom: string; quantite?: number; unite?: string }>;
      };
      const recette = {
        id: prochainRecetteId++,
        nom: payload.nom,
        description: payload.description ?? "",
        instructions: payload.instructions ?? "",
        ingredients: (payload.ingredients ?? []).map((ingredient) => ({
          nom: ingredient.nom,
          quantite: ingredient.quantite ?? 1,
          unite: ingredient.unite ?? "pièce",
        })),
        categorie: "Plat",
        difficulte: "facile",
        temps_preparation: 20,
        temps_cuisson: 35,
        portions: 4,
      };
      recettes.unshift(recette);

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(recette),
      });
      return;
    }

    const matchRecetteDetail = path.match(/^\/api\/v1\/recettes\/(\d+)$/);
    if (matchRecetteDetail && method === "GET") {
      const recette = recetteParId(Number(matchRecetteDetail[1]));
      await route.fulfill({
        status: recette ? 200 : 404,
        contentType: "application/json",
        body: JSON.stringify(recette ?? { detail: "Recette introuvable" }),
      });
      return;
    }

    if (path === "/api/v1/recettes/planifiees-semaine" && method === "GET") {
      const planifiees = Array.from(recettesPlanifiees)
        .map((id) => recetteParId(id))
        .filter(Boolean);
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(planifiees),
      });
      return;
    }

    const matchPlanifierRecette = path.match(/^\/api\/v1\/recettes\/(\d+)\/planifier-semaine$/);
    if (matchPlanifierRecette && method === "POST") {
      recettesPlanifiees.add(Number(matchPlanifierRecette[1]));
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) });
      return;
    }

    if (matchPlanifierRecette && method === "DELETE") {
      recettesPlanifiees.delete(Number(matchPlanifierRecette[1]));
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) });
      return;
    }

    if (path === "/api/v1/planning/semaine" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(construirePlanning()),
      });
      return;
    }

    if (path === "/api/v1/planning/conflits" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ items: [], resume: "Aucun conflit", total: 0 }),
      });
      return;
    }

    if (path === "/api/v1/planning/nutrition-hebdo" && method === "GET") {
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
      return;
    }

    if (path === "/api/v1/planning/suggestions-rapides" && method === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      return;
    }

    if (path === "/api/v1/flux/cuisine-3-clics" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ etape_actuelle: "aucune_action", planning: null }),
      });
      return;
    }

    if (path === "/api/v1/famille/evenements" && method === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      return;
    }

    if (path === "/api/v1/calendriers/evenements" && method === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      return;
    }

    if (path === "/api/v1/courses/generer-depuis-planning" && method === "POST") {
      const recette = recetteParId(Array.from(recettesPlanifiees)[0]);
      const listeId = prochainListeId++;
      const articles = (recette?.ingredients ?? []).map((ingredient) => ({
        id: prochainArticleId++,
        nom: ingredient.nom,
        quantite: ingredient.quantite,
        unite: ingredient.unite,
        categorie: "Légumes",
        est_coche: false,
      }));

      const detail = {
        id: listeId,
        nom: "Courses de la semaine",
        etat: "brouillon" as const,
        date_creation: "2026-03-23T08:00:00Z",
        est_terminee: false,
        nombre_articles: articles.length,
        nombre_coche: 0,
        articles,
      };
      detailsListes.set(listeId, detail);
      listes.unshift({
        id: listeId,
        nom: detail.nom,
        etat: detail.etat,
        date_creation: detail.date_creation,
        est_terminee: false,
        nombre_articles: detail.nombre_articles,
        nombre_coche: 0,
      });

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          liste_id: listeId,
          nom: detail.nom,
          total_articles: articles.length,
          articles_en_stock: 0,
          contexte: { nb_invites: 0, evenements: [], multiplicateur_quantites: 1 },
          articles: articles.map((article) => ({
            nom: article.nom,
            quantite: article.quantite,
            unite: article.unite,
            rayon: article.categorie,
            en_stock: 0,
          })),
          par_rayon: { "Légumes": articles.length },
        }),
      });
      return;
    }

    if (path === "/api/v1/courses/recurrents-suggeres" && method === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ suggestions: [], total: 0 }) });
      return;
    }

    if (path.includes("/bio-local") && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ liste_id: 0, mois: "2026-03", suggestions: [], nb_en_saison: 0 }),
      });
      return;
    }

    if (path === "/api/v1/courses/predictions" && method === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      return;
    }

    if (path === "/api/v1/courses" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(listes),
      });
      return;
    }

    if (path === "/api/v1/courses" && method === "POST") {
      const payload = request.postDataJSON() as { nom?: string };
      const listeId = prochainListeId++;
      const detail = {
        id: listeId,
        nom: payload.nom?.trim() || "Nouvelle liste",
        etat: "brouillon" as const,
        date_creation: "2026-03-23T08:05:00Z",
        est_terminee: false,
        nombre_articles: 0,
        nombre_coche: 0,
        articles: [],
      };
      detailsListes.set(listeId, detail);
      listes.unshift({ ...detail });

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: listeId }),
      });
      return;
    }

    const matchConfirmerListe = path.match(/^\/api\/v1\/courses\/(\d+)\/confirmer$/);
    if (matchConfirmerListe && method === "POST") {
      const listeId = Number(matchConfirmerListe[1]);
      const detail = listeParId(listeId);
      if (detail) {
        detail.etat = "confirmee";
        synchroniserResumeListe(listeId);
      }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) });
      return;
    }

    const matchValiderListe = path.match(/^\/api\/v1\/courses\/(\d+)\/valider$/);
    if (matchValiderListe && method === "POST") {
      const listeId = Number(matchValiderListe[1]);
      const detail = listeParId(listeId);
      if (detail) {
        for (const article of detail.articles.filter((item) => item.est_coche)) {
          const inventaireExistant = inventaire.find((item) => item.nom === article.nom);
          if (inventaireExistant) {
            inventaireExistant.quantite += article.quantite;
          } else {
            inventaire.push({
              id: article.id,
              nom: article.nom,
              categorie: article.categorie,
              quantite: article.quantite,
              unite: article.unite,
              emplacement: "Frigo",
              est_bas: false,
              est_expire: false,
            });
          }
        }
        detail.etat = "terminee";
        detail.est_terminee = true;
        synchroniserResumeListe(listeId);
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "Courses validées", id: listeId }),
      });
      return;
    }

    const matchDetailListe = path.match(/^\/api\/v1\/courses\/(\d+)$/);
    if (matchDetailListe && method === "GET") {
      const detail = listeParId(Number(matchDetailListe[1]));
      await route.fulfill({
        status: detail ? 200 : 404,
        contentType: "application/json",
        body: JSON.stringify(detail ?? { detail: "Liste introuvable" }),
      });
      return;
    }

    const matchItemListe = path.match(/^\/api\/v1\/courses\/(\d+)\/items\/(\d+)$/);
    if (matchItemListe && method === "PUT") {
      const listeId = Number(matchItemListe[1]);
      const articleId = Number(matchItemListe[2]);
      const payload = request.postDataJSON() as { coche?: boolean };
      const detail = listeParId(listeId);
      const article = detail?.articles.find((item) => item.id === articleId);
      if (detail && article) {
        article.est_coche = Boolean(payload.coche);
        synchroniserResumeListe(listeId);
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(article ?? { detail: "Article introuvable" }),
      });
      return;
    }

    if (path === "/api/v1/inventaire" && method === "GET") {
      const emplacement = url.searchParams.get("emplacement");
      const articles = emplacement
        ? inventaire.filter((article) => article.emplacement === emplacement)
        : inventaire;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(articles),
      });
      return;
    }

    if (path === "/api/v1/inventaire/alertes" && method === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      return;
    }

    if (path.startsWith("/api/v1/telegram/") && method === "POST") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({}),
    });
  });
}

test.describe("Cuisine - Parcours complet", () => {
  test("7.1 - Cuisine complet: créer recette → planifier semaine → générer liste courses → cocher acheté → inventaire mis à jour", async ({
    page,
  }) => {
    await configurerContexteCuisineComplet(page);

    await page.goto("/cuisine/recettes/nouveau");
    await expect(page.getByRole("heading", { name: /nouvelle recette/i })).toBeVisible();

    await page.getByLabel(/Nom/i).fill("Gratin sprint 3");
    await page.getByLabel(/Description/i).fill("Recette de test sprint 3");
    await page.getByLabel(/Instructions/i).fill("Mélanger, cuire et servir.");
    await page.getByPlaceholder("Ingrédient").fill("Pommes de terre");
    await page.getByPlaceholder("Qté").fill("6");
    await page.getByPlaceholder("Unité").fill("pièce");

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/api/v1/recettes") &&
          response.request().method() === "POST" &&
          response.status() === 200
      ),
      page.getByRole("button", { name: /Créer la recette/i }).click(),
    ]);

    await expect(page).toHaveURL(/\/cuisine\/recettes\/101/);

    await page.goto("/cuisine/recettes");
    await expect(page.getByRole("heading", { name: /Recettes/i })).toBeVisible();
    await expect(page.getByText("Gratin sprint 3")).toBeVisible();

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/planifier-semaine") &&
          response.request().method() === "POST" &&
          response.status() === 200
      ),
      page.locator('button[title="Ajouter au menu de la semaine"]').first().click(),
    ]);

    await page.goto("/cuisine/planning");
    await expect(page.getByRole("heading", { name: /Planning repas/i })).toBeVisible();
    await expect(page.getByText("Gratin sprint 3")).toBeVisible();

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/courses/generer-depuis-planning") &&
          response.request().method() === "POST" &&
          response.status() === 200
      ),
      page.getByRole("button", { name: /^Courses$/i }).click(),
    ]);

    await page.goto("/cuisine/courses");
    await expect(page.getByRole("heading", { name: /Courses/i })).toBeVisible();
    await page.getByRole("button", { name: /Courses de la semaine/i }).click();

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/confirmer") &&
          response.request().method() === "POST" &&
          response.status() === 200
      ),
      page.getByRole("button", { name: /Confirmer la liste/i }).click(),
    ]);

    await page.getByRole("button", { name: /Pommes de terre/i }).click();
    await expect(page.getByText(/Complétés \(1\)/i)).toBeVisible();

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/valider") &&
          response.request().method() === "POST" &&
          response.status() === 200
      ),
      page.getByRole("button", { name: /Valider courses/i }).click(),
    ]);

    await page.goto("/cuisine/inventaire");
    await expect(page.getByRole("heading", { name: /Inventaire/i })).toBeVisible();
    await expect(page.getByText("Pommes de terre")).toBeVisible();
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
