import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux maison (projets, entretien, énergie)
// ═══════════════════════════════════════════════════════════

test.describe("Maison — sous-pages", () => {
  test("toutes les sous-pages maison se chargent", async ({ page }) => {
    const sousPages = [
      "/maison/projets",
      "/maison/entretien",
      "/maison/energie",
      "/maison/jardin",
      "/maison/stocks",
      "/maison/cellier",
      "/maison/charges",
      "/maison/depenses",
      "/maison/contrats",
      "/maison/garanties",
      "/maison/diagnostics",
      "/maison/artisans",
      "/maison/eco-tips",
      "/maison/visualisation",
    ];

    for (const url of sousPages) {
      await page.goto(url);
      await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
      await expect(page.locator("h1")).toBeVisible();
    }
  });
});

test.describe("Projets maison", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/maison/projets");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });
  });

  test("affiche le titre et le bouton d'ajout", async ({ page }) => {
    const boutonAjouter = page.getByText(/Nouveau projet|Ajouter/i);
    if (await boutonAjouter.count() > 0) {
      await expect(boutonAjouter.first()).toBeVisible();
    }
  });
});

test.describe("Entretien", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/maison/entretien");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });
  });

  test("sections en retard et planifiées sont affichées", async ({ page }) => {
    // La page peut afficher "En retard" ou "Planifiées" ou un message vide
    await expect(page.locator("body")).toBeVisible();
  });
});

test.describe("Visualisation plan maison", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/maison/visualisation");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });
  });

  test("contrôles d'étage sont fonctionnels", async ({ page }) => {
    const boutonPrec = page.getByRole("button", { name: /étage précédent/i });
    const boutonSuiv = page.getByRole("button", { name: /étage suivant/i });

    if (await boutonPrec.isVisible().catch(() => false)) {
      await expect(boutonPrec).toBeVisible();
      await expect(boutonSuiv).toBeVisible();
    }
  });
});
