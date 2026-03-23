import { test, expect } from "@playwright/test";

test.describe("Navigation modules", () => {
  test("navigation vers les hubs principaux", async ({ page }) => {
    // Cuisine hub
    await page.goto("/cuisine");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();

    // Famille hub
    await page.goto("/famille");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();

    // Maison hub
    await page.goto("/maison");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();

    // Jeux hub
    await page.goto("/jeux");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();

    // Outils hub
    await page.goto("/outils");
    await expect(page.locator("body")).toBeVisible();
    await expect(page.locator("h1")).toBeVisible();
  });

  test("navigation vers les sous-pages cuisine", async ({ page }) => {
    const pages = [
      "/cuisine/recettes",
      "/cuisine/planning",
      "/cuisine/courses",
      "/cuisine/inventaire",
    ];

    for (const url of pages) {
      await page.goto(url);
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("navigation vers les sous-pages famille", async ({ page }) => {
    const pages = [
      "/famille/jules",
      "/famille/activites",
      "/famille/budget",
      "/famille/routines",
    ];

    for (const url of pages) {
      await page.goto(url);
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("navigation vers les sous-pages maison", async ({ page }) => {
    const pages = [
      "/maison/projets",
      "/maison/entretien",
      "/maison/jardin",
      "/maison/energie",
    ];

    for (const url of pages) {
      await page.goto(url);
      await expect(page.locator("body")).toBeVisible();
    }
  });
});

test.describe("Pages outils (client-side, sans auth)", () => {
  test("convertisseur fonctionne", async ({ page }) => {
    await page.goto("/outils/convertisseur");
    await expect(page.locator("h1")).toContainText(/Convertisseur/i);

    // Onglets visibles
    await expect(page.getByText("Masse")).toBeVisible();
    await expect(page.getByText("Volume")).toBeVisible();
  });

  test("minuteur fonctionne", async ({ page }) => {
    await page.goto("/outils/minuteur");
    await expect(page.locator("h1")).toContainText(/Minuteur/i);

    // Bouton démarrer visible
    await expect(page.getByText(/Démarrer/)).toBeVisible();
  });

  test("euromillions fonctionne", async ({ page }) => {
    await page.goto("/jeux/euromillions");
    await expect(page.getByText(/Euromillions/i)).toBeVisible();
    await expect(page.getByText(/Nouvelle grille/)).toBeVisible();
  });
});

test.describe("Responsive design", () => {
  test("affichage mobile (375px)", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/outils/convertisseur");
    await expect(page.locator("h1")).toBeVisible();
  });

  test("affichage tablette (768px)", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto("/outils/convertisseur");
    await expect(page.locator("h1")).toBeVisible();
  });

  test("affichage desktop (1280px)", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("/outils/convertisseur");
    await expect(page.locator("h1")).toBeVisible();
  });
});

test.describe("PWA", () => {
  test("manifest.json est accessible", async ({ page }) => {
    const response = await page.goto("/manifest.json");
    expect(response?.status()).toBe(200);

    const manifest = await response?.json();
    expect(manifest.name).toBeTruthy();
    expect(manifest.icons).toBeDefined();
  });
});
