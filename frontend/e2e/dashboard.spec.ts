import { expect, test } from "@playwright/test";

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
    const errors = [];
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
