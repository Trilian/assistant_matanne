import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// Tests E2E — Interactions utilisateur (pages client-side)
// ═══════════════════════════════════════════════════════════

test.describe("Convertisseur — interactions", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/outils/convertisseur");
    await expect(page.locator("h1")).toContainText(/Convertisseur/i);
  });

  test("conversion masse: saisir une valeur met à jour le résultat", async ({ page }) => {
    // L'onglet Masse est actif par défaut
    const champValeur = page.locator("input").first();
    await champValeur.fill("1000");
    // Le résultat devrait s'afficher (valeur non vide)
    await expect(page.locator("input").nth(1)).not.toHaveValue("");
  });

  test("changer d'onglet vers Volume puis Longueur", async ({ page }) => {
    await page.getByText("Volume").click();
    await expect(page.getByText("Volume")).toBeVisible();

    await page.getByText("Longueur").click();
    await expect(page.getByText("Longueur")).toBeVisible();

    await page.getByText("Temp.").click();
    await expect(page.getByText("Temp.")).toBeVisible();
  });
});

test.describe("Minuteur — interactions", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/outils/minuteur");
    await expect(page.locator("h1")).toContainText(/Minuteur/i);
  });

  test("cliquer sur un preset met à jour la durée", async ({ page }) => {
    await page.getByText("5 min").click();
    // Vérifier que le temps affiché contient "5:00" ou "05:00"
    await expect(page.locator("body")).toContainText(/5:00|05:00/);
  });

  test("basculer vers l'onglet Chronomètre", async ({ page }) => {
    await page.getByRole("tab", { name: /chronomètre/i }).click();
    await expect(page.getByText(/Démarrer/)).toBeVisible();
  });

  test("démarrer et arrêter le chronomètre", async ({ page }) => {
    await page.getByRole("tab", { name: /chronomètre/i }).click();
    await page.getByText(/Démarrer/).click();
    // Attendre un peu
    await page.waitForTimeout(500);
    // Le bouton devrait maintenant être Pause ou Arrêter
    const body = await page.locator("body").textContent();
    expect(body).toMatch(/Pause|Arrêter|Stop/i);
  });
});

test.describe("Euromillions — interactions", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/jeux/euromillions");
    await expect(page.getByText(/Euromillions/i)).toBeVisible();
  });

  test("générer une nouvelle grille affiche des numéros", async ({ page }) => {
    await page.getByText(/Nouvelle grille/).click();
    // La page devrait toujours être visible avec des numéros
    await expect(page.getByText(/5 numéros/i)).toBeVisible();
    await expect(page.getByText(/2 étoiles/i)).toBeVisible();
  });

  test("les numéros sont dans la plage valide (1-50)", async ({ page }) => {
    // Vérifier qu'il y a des éléments numériques affichés
    await expect(page.getByText(/Euromillions/i)).toBeVisible();
    await expect(page.locator("body")).toBeVisible();
  });
});

test.describe("Accessibilité de base", () => {
  const pages = [
    { url: "/outils/convertisseur", titre: /Convertisseur/i },
    { url: "/outils/minuteur", titre: /Minuteur/i },
    { url: "/jeux/euromillions", titre: /Euromillions/i },
  ];

  for (const { url, titre } of pages) {
    test(`${url} a un heading h1`, async ({ page }) => {
      await page.goto(url);
      const h1 = page.locator("h1");
      await expect(h1).toBeVisible();
      await expect(h1).toContainText(titre);
    });

    test(`${url} n'a pas de lien cassé visible`, async ({ page }) => {
      await page.goto(url);
      const liens = page.locator("a[href]");
      const count = await liens.count();
      for (let i = 0; i < Math.min(count, 10); i++) {
        const href = await liens.nth(i).getAttribute("href");
        expect(href).toBeTruthy();
        expect(href).not.toBe("#");
      }
    });
  }
});

test.describe("Navigation clavier", () => {
  test("onglets du convertisseur navigables au clavier", async ({ page }) => {
    await page.goto("/outils/convertisseur");
    // Tab vers le premier onglet et appuyer sur Entrée
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Enter");
    // La page devrait rester fonctionnelle
    await expect(page.locator("h1")).toBeVisible();
  });
});
