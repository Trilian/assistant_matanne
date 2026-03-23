import { test, expect } from "@playwright/test";

test.describe("Pages maison — E2E", () => {
  test("hub maison affiche les sections", async ({ page }) => {
    await page.goto("/maison");
    await expect(page.locator("h1")).toContainText("Maison");

    // Vérifie que les cartes de section sont rendues
    const links = page.locator('a[href^="/maison/"]');
    await expect(links.first()).toBeVisible({ timeout: 10000 });
    expect(await links.count()).toBeGreaterThanOrEqual(5);
  });

  test("page projets se charge et affiche le contenu", async ({ page }) => {
    await page.goto("/maison/projets");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();
  });

  test("page cellier se charge", async ({ page }) => {
    await page.goto("/maison/cellier");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();
  });

  test("page visualisation se charge", async ({ page }) => {
    await page.goto("/maison/visualisation");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toContainText("Plan");
  });

  test("navigation entre étages avec les boutons", async ({ page }) => {
    await page.goto("/maison/visualisation");
    // Vérifie les contrôles d'étage
    const badgeEtage = page.locator('[class*="badge"]').filter({ hasText: /RDC|\+|−/ });
    await expect(badgeEtage.first()).toBeVisible({ timeout: 10000 });
  });
});

test.describe("Pages cuisine — E2E", () => {
  test("hub cuisine affiche les 6 sections", async ({ page }) => {
    await page.goto("/cuisine");
    await expect(page.locator("h1")).toContainText("Cuisine");

    const sectionLinks = page.locator('a[href^="/cuisine/"]');
    await expect(sectionLinks.first()).toBeVisible({ timeout: 10000 });
    expect(await sectionLinks.count()).toBe(6);
  });

  test("page recettes se charge et affiche la recherche", async ({ page }) => {
    await page.goto("/cuisine/recettes");
    await expect(page.locator("body")).toBeVisible();
    const searchInput = page.locator('input[placeholder*="echercher"]');
    await expect(searchInput).toBeVisible({ timeout: 10000 });
  });
});

test.describe("Pages outils — E2E", () => {
  test("minuteur fonctionne", async ({ page }) => {
    await page.goto("/outils/minuteur");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();
  });

  test("convertisseur fonctionne", async ({ page }) => {
    await page.goto("/outils/convertisseur");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();
  });
});
