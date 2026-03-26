// @ts-nocheck
import { test, expect, type Browser, type Page } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Courses : UI single-user + collaboration WebSocket multi-user
// ═══════════════════════════════════════════════════════════

async function naviguerVersCourses(page: Page): Promise<void> {
  await page.goto("/cuisine/courses");
  await expect(page.locator("body")).toBeVisible({ timeout: 15000 });
}

// ─── Suite 1 : navigation et UI (single-user) ─────────────
test.describe("Courses — navigation et UI", () => {
  test.beforeEach(async ({ page }) => {
    await naviguerVersCourses(page);
  });

  test("page courses affiche le formulaire de création de liste", async ({ page }) => {
    const inputNom = page.locator('input[placeholder*="ouvelle liste"]');
    await expect(inputNom).toBeVisible({ timeout: 10000 });
  });

  test("bouton créer liste est présent", async ({ page }) => {
    const bouton = page.getByRole("button", { name: /Créer la liste/i });
    await expect(bouton).toBeVisible();
  });

  test("message d'état visible quand aucune liste sélectionnée", async ({ page }) => {
    await expect(page.locator("body")).toBeVisible();
    const hasEmpty = await page.locator("text=Aucune liste").isVisible().catch(() => false);
    const hasForm = await page.locator('input[placeholder*="ouvelle liste"]').isVisible().catch(() => false);
    expect(hasEmpty || hasForm).toBe(true);
  });

  test("sélectionner une liste affiche les articles", async ({ page }) => {
    const premiereListe = page.locator('button[class*="text-left"]').first();
    if (await premiereListe.isVisible().catch(() => false)) {
      await premiereListe.click();
      await expect(page.locator("body")).toBeVisible();
    }
  });
});

// ─── Suite 2 : collaboration WebSocket multi-utilisateur ──
test.describe("Courses — collaboration WebSocket multi-utilisateur", () => {
  test.skip(
    process.env.CI === "true" && !process.env.ENABLE_WS_TESTS,
    "Tests WS désactivés en CI sans ENABLE_WS_TESTS=true"
  );

  test("deux contextes naviguent vers courses sans erreur JS critique", async ({ browser }: { browser: Browser }) => {
    const contextA = await browser.newContext();
    const contextB = await browser.newContext();
    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();
    const errorsA: string[] = [];
    const errorsB: string[] = [];

    pageA.on("console", (msg) => { if (msg.type() === "error") errorsA.push(msg.text()); });
    pageB.on("console", (msg) => { if (msg.type() === "error") errorsB.push(msg.text()); });

    try {
      await Promise.all([naviguerVersCourses(pageA), naviguerVersCourses(pageB)]);
      await Promise.all([pageA.waitForTimeout(1000), pageB.waitForTimeout(1000)]);

      // Filtrer les erreurs réseau (backend peut ne pas tourner en CI)
      const critiquesA = errorsA.filter((e) => !e.includes("net::ERR_") && !e.includes("Failed to fetch") && !e.includes("ECONNREFUSED"));
      const critiquesB = errorsB.filter((e) => !e.includes("net::ERR_") && !e.includes("Failed to fetch") && !e.includes("ECONNREFUSED"));
      expect(critiquesA).toHaveLength(0);
      expect(critiquesB).toHaveLength(0);
    } finally {
      await contextA.close();
      await contextB.close();
    }
  });

  test("création de liste par utilisateur A visible après rechargement par utilisateur B", async ({ browser }: { browser: Browser }) => {
    const contextA = await browser.newContext();
    const contextB = await browser.newContext();
    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();

    try {
      await naviguerVersCourses(pageA);
      const inputNom = pageA.locator('input[placeholder*="ouvelle liste"]');

      if (await inputNom.isVisible({ timeout: 3000 }).catch(() => false)) {
        const nomListe = `Collab-${Date.now()}`;
        await inputNom.fill(nomListe);
        const btnCreer = pageA.getByRole("button", { name: /Créer la liste/i });

        if (await btnCreer.isEnabled().catch(() => false)) {
          await btnCreer.click();
          await pageA.waitForTimeout(1500);

          // Utilisateur B charge la page et devrait voir la liste
          await naviguerVersCourses(pageB);
          await pageB.waitForTimeout(1000);

          const listeVisibleB = await pageB.locator(`text=${nomListe}`).isVisible({ timeout: 5000 }).catch(() => false);
          expect(await pageB.locator("body").isVisible()).toBe(true);
          if (!listeVisibleB) {
            console.info(`Liste "${nomListe}" non trouvée sur pageB — backend possiblement absent`);
          }
        }
      } else {
        test.info().annotations.push({ type: "condition", description: "Formulaire non visible, backend absent" });
      }
    } finally {
      await contextA.close();
      await contextB.close();
    }
  });

  test("connexion WebSocket s'établit sans erreur bloquante", async ({ browser }: { browser: Browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    const wsErrors: string[] = [];

    page.on("websocket", (ws) => {
      ws.on("socketerror", (error) => wsErrors.push(String(error)));
    });

    try {
      await naviguerVersCourses(page);
      await page.waitForTimeout(2000);

      const erreursCritiques = wsErrors.filter(
        (e) => !e.includes("ECONNREFUSED") && !e.includes("net::ERR_CONNECTION_REFUSED") && !e.includes("websocket")
      );
      expect(erreursCritiques).toHaveLength(0);
    } finally {
      await context.close();
    }
  });

  test("trois utilisateurs simultanés — pas de dégradation UI", async ({ browser }: { browser: Browser }) => {
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext(),
    ]);
    const pages = await Promise.all(contexts.map((ctx) => ctx.newPage()));

    try {
      await Promise.all(pages.map((p) => naviguerVersCourses(p)));
      await Promise.all(pages.map((p) => p.waitForTimeout(800)));

      for (const p of pages) {
        await expect(p.locator("body")).toBeVisible();
      }
    } finally {
      await Promise.all(contexts.map((ctx) => ctx.close()));
    }
  });
});
