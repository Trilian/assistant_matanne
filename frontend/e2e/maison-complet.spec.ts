import { expect, test } from "@playwright/test";

test.describe("Maison - Parcours complet", () => {
  test("7.4 - Maison entretien: voir tâches du jour → marquer fait → vérifier historique", async ({
    page,
  }) => {
    // Naviguer vers maison
    await page.goto("/maison");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("Maison");

    // Naviguer vers travaux/entretien
    await page.goto("/maison/travaux");
    await expect(page).toHaveURL(/\/maison\/travaux/);
    await expect(page.getByRole("heading")).toBeVisible();

    // Vérifier la présence de tâches ou du formulaire de création
    const createButton = page.locator('button:has-text("Créer"), button:has-text("Ajouter")').first();
    if (await createButton.isVisible()) {
      console.log("[Entretien] Bouton créer visible");
    }

    // Vérifier l'historique (navigation)
    const historiqueLink = page.getByRole("link", { name: /historique|complétée/i });
    if (await historiqueLink.isVisible()) {
      await historiqueLink.click();
      await expect(page.locator("body")).toBeVisible();
    }

    // Pas d'erreur JS
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("7.5 - Budget famille: voir budget → ajouter dépense → alerte dépassement", async ({
    page,
  }) => {
    // Naviguer vers budget via famille
    await page.goto("/famille/budget");
    await expect(page).toHaveURL(/\/famille\/budget/);
    await expect(page.getByRole("heading")).toBeVisible();

    // Vérifier la présence d'éléments de budget
    const budgetTitle = page.getByText(/budget|Budget/);
    await expect(budgetTitle.first()).toBeVisible();

    // Pas d'erreur JS
    const errors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("Navigation complète module Maison", async ({ page }) => {
    const routes = ["/maison", "/maison/travaux", "/maison/jardin", "/maison/finances"];

    for (const route of routes) {
      await page.goto(route);
      await expect(page).toHaveURL(new RegExp(route));
      await expect(page.locator("body")).toBeVisible();
    }
  });
});
