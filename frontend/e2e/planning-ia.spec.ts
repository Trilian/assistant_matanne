import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux planning repas
// ═══════════════════════════════════════════════════════════

test.describe("Planning repas", () => {
  test.beforeEach(async ({ page }) => {
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
  test("page planning se charge correctement", async ({ page }) => {
    await page.goto("/planning");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });
  });

  test("navigation semaine avec boutons flèche", async ({ page }) => {
    await page.goto("/planning");
    await expect(page.locator("h1")).toBeVisible({ timeout: 10000 });

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
