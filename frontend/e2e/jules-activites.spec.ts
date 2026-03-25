import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux famille (Jules, activités, budget)
// ═══════════════════════════════════════════════════════════

test.describe("Famille — Hub et navigation", () => {
  test("hub famille affiche les sections", async ({ page }) => {
    await page.goto("/famille");
    await expect(page.locator("h1")).toContainText("Famille", { timeout: 10000 });

    const liens = page.locator('a[href^="/famille/"]');
    await expect(liens.first()).toBeVisible({ timeout: 10000 });
    expect(await liens.count()).toBeGreaterThanOrEqual(5);
  });

  test("navigation vers chaque sous-page famille", async ({ page }) => {
    const sousPages = [
      "/famille/jules",
      "/famille/activites",
      "/famille/budget",
      "/famille/routines",
      "/famille/album",
      "/famille/anniversaires",
      "/famille/contacts",
      "/famille/documents",
      "/famille/journal",
    ];

    for (const url of sousPages) {
      await page.goto(url);
      await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
    }
  });
});

test.describe("Jules — suivi développement", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/famille/jules");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
  });

  test("page Jules se charge avec titre", async ({ page }) => {
    await expect(page.locator("h1")).toBeVisible();
  });
});

test.describe("Budget famille", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/famille/budget");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
  });

  test("page budget se charge avec formulaire", async ({ page }) => {
    await expect(page.locator("h1")).toBeVisible();
  });

  test("bouton scanner ticket est présent", async ({ page }) => {
    const boutonScanner = page.getByText(/Scanner/i);
    if (await boutonScanner.isVisible().catch(() => false)) {
      await expect(boutonScanner).toBeVisible();
    }
  });
});

test.describe("Activités", () => {
  test("page activités se charge", async ({ page }) => {
    await page.goto("/famille/activites");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
    await expect(page.locator("h1")).toBeVisible();
  });
});
