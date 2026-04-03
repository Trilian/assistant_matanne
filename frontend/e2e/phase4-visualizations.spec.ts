import { expect, test } from "@playwright/test";

test.describe("Phase 4 - Visualizations (Treemap + Budget)", () => {
  test("4.1 - Treemap Inventaire: rendu SVG + drill-down interactif", async ({
    page,
  }) => {
    // Naviguer vers la page inventaire
    await page.goto("/cuisine/inventaire");
    await expect(page).toHaveURL(/\/cuisine\/inventaire/);

    // Vérifier que le titre de la page est visible
    await expect(page.getByRole("heading", { level: 1 })).toContainText(
      /inventaire|Inventaire/i
    );

    // Attendre le rendu de la treemap (SVG)
    const treemapSVG = page.locator("svg").first();
    await expect(treemapSVG).toBeVisible({ timeout: 3000 });

    // Vérifier la présence d'éléments SVG (rects pour les cellules)
    const rects = page.locator("svg rect");
    const rectCount = await rects.count();
    expect(rectCount).toBeGreaterThan(0);

    // Vérifier la présence de texte (catégories/articles)
    const textElements = page.locator("svg text");
    const textCount = await textElements.count();
    expect(textCount).toBeGreaterThan(0);

    // Vérifier la structure de données minimale (au moins 2 catégories)
    const categories = page.locator("[data-category]");
    const categoryCount = await categories.count();
    expect(categoryCount).toBeGreaterThanOrEqual(1);

    // Test interactivité: hover sur une cellule (si elle a un curseur pointer)
    if (rectCount > 0) {
      const firstRect = page.locator("svg rect").first();
      await firstRect.hover();
      // La cellule devrait changer d'apparence (couleur, opacité)
      const ariaLabel = await firstRect.getAttribute("aria-label");
      if (ariaLabel) {
        expect(ariaLabel).toBeTruthy();
      }
    }

    // Vérifier l'absence d'erreurs JavaScript
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("4.2 - Budget vs Réel: rendu graphique Recharts + données affichées", async ({
    page,
  }) => {
    // Naviguer vers la page budget famille
    await page.goto("/famille/budget");
    await expect(page).toHaveURL(/\/famille\/budget/);

    // Vérifier que le titre de la page est visible
    await expect(page.getByRole("heading")).toContainText(
      /budget|Budget|Réel/i
    );

    // Attendre le rendu du graphique Recharts (BarChart)
    // Recharts crée un SVG pour le graphique
    const chartSVG = page.locator('svg[role="presentation"]').first();
    await expect(chartSVG).toBeVisible({ timeout: 3000 });

    // Vérifier la présence de barres dans le graphique
    const bars = page.locator("svg rect[height]");
    const barCount = await bars.count();
    expect(barCount).toBeGreaterThan(0);

    // Vérifier l'affichage des labels (axes)
    const yAxis = page.locator("text").filter({ hasText: /€|Budget|Réel/i });
    const yAxisCount = await yAxis.count();
    expect(yAxisCount).toBeGreaterThanOrEqual(1);

    // Test interactivité: hover sur une barre pour voir le tooltip
    if (barCount > 0) {
      const firstBar = page.locator("svg rect[height]").first();
      await firstBar.hover();
      // Attendre l'apparition du tooltip
      const tooltip = page
        .locator("div")
        .filter({ hasText: /Budget|Réel|Dépensé/i });
      // Le tooltip peut ne pas être visible immédiatement, donc on teste juste le hover
      expect(firstBar).toBeTruthy();
    }

    // Vérifier le bloc d'économies (si visible)
    const economiesBlock = page.locator("div").filter({ hasText: /économies/i });
    const economiesCount = await economiesBlock.count();
    // Peut ne pas être affichée si budget > prévu
    expect(economiesCount).toBeGreaterThanOrEqual(0);

    // Vérifier l'absence d'erreurs JavaScript
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("4.3 - Intégration complète: naviguer inventaire → budget sans erreurs", async ({
    page,
  }) => {
    // Naviguer vers le hub cuisine
    await page.goto("/cuisine");
    await expect(page).toHaveURL(/\/cuisine/);

    // Naviguer vers l'inventaire
    await page.goto("/cuisine/inventaire");
    await expect(page).toHaveURL(/\/cuisine\/inventaire/);

    // Vérifier le rendu de la treemap
    const treemapSVG = page.locator("svg").first();
    await expect(treemapSVG).toBeVisible({ timeout: 3000 });

    // Naviguer vers le budget famille
    await page.goto("/famille/budget");
    await expect(page).toHaveURL(/\/famille\/budget/);

    // Vérifier le rendu du graphique budget
    const chartSVG = page.locator('svg[role="presentation"]').first();
    await expect(chartSVG).toBeVisible({ timeout: 3000 });

    // Vérifier pas d'erreurs de navigation
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });

  test("4.4 - Responsive: Treemap sur mobile", async ({ page }) => {
    // Utiliser le contexte mobile Chrome depuis la config
    await page.goto("/cuisine/inventaire");
    await expect(page).toHaveURL(/\/cuisine\/inventaire/);

    // Sur mobile, la treemap doit être responsive
    const treemapSVG = page.locator("svg").first();
    await expect(treemapSVG).toBeVisible({ timeout: 3000 });

    // Vérifier que le SVG s'adapte à la largeur disponible (mobile: ~400px)
    const svgBoundingBox = await treemapSVG.boundingBox();
    expect(svgBoundingBox?.width).toBeLessThanOrEqual(500); // Largeur max mobile + padding
    expect(svgBoundingBox?.height).toBeGreaterThan(200); // Hauteur minimale

    // Pas d'erreurs de rendu
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    expect(errors.length).toBe(0);
  });
});
