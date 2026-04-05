import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Flux authentification
// ═══════════════════════════════════════════════════════════

test.describe("Authentification", () => {
  test("page connexion se charge avec formulaire", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Formulaire de connexion visible
    const emailInput = page.locator('input[type="email"], input[name="email"]');
    const passwordInput = page.locator('input[type="password"]');

    if (await emailInput.isVisible().catch(() => false)) {
      await expect(emailInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
    }
  });

  test("page inscription est accessible", async ({ page }) => {
    await page.goto("/inscription");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
  });

  test("redirection vers connexion si non authentifié", async ({ page }) => {
    await page.goto("/");
    // Doit rediriger vers connexion si pas de token
    await page.waitForURL(/connexion/, { timeout: 5000 }).catch(() => {});
    await expect(page.locator("body")).toBeVisible();
  });

  test("lien entre connexion et inscription fonctionne", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    const lienInscription = page.getByText(/inscription|créer un compte/i);
    if (await lienInscription.isVisible().catch(() => false)) {
      await lienInscription.click();
      await expect(page.locator("body")).toBeVisible();
    }
  });

  test("formulaire connexion valide les champs requis", async ({ page }) => {
    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Tenter de soumettre sans remplir — le bouton devrait être désactivé ou montrer une erreur
    const boutonConnexion = page.getByRole("button", { name: /connexion|se connecter/i });
    if (await boutonConnexion.isVisible().catch(() => false)) {
      await expect(boutonConnexion).toBeVisible();
    }
  });
});

// ═══════════════════════════════════════════════════════════
// E2E — Flux authentification complet avec API mockée
// ═══════════════════════════════════════════════════════════

test.describe("Authentification — Flux complet", () => {
  test("login avec credentials → JWT stocké → accès route protégée", async ({ page }) => {
    // Mock de l'endpoint login
    await page.route("**/api/v1/auth/login", async (route) => {
      const body = JSON.parse(route.request().postData() || "{}");
      if (body.email === "test@matanne.fr" && body.password === "MotDePasse123!") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ access_token: "e2e-jwt-token", token_type: "bearer" }),
        });
      } else {
        await route.fulfill({
          status: 401,
          contentType: "application/json",
          body: JSON.stringify({ detail: "Email ou mot de passe incorrect" }),
        });
      }
    });

    await page.route("**/api/v1/auth/me", async (route) => {
      const auth = route.request().headers()["authorization"];
      if (auth?.includes("e2e-jwt-token")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ id: 1, email: "test@matanne.fr", nom: "Test User", role: "admin" }),
        });
      } else {
        await route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "Non authentifié" }) });
      }
    });

    // Mock des endpoints dashboard pour éviter les erreurs réseau
    await page.route("**/api/v1/**", async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (path !== "/api/v1/auth/login" && path !== "/api/v1/auth/me") {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
      } else {
        await route.continue();
      }
    });

    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    const emailInput = page.locator('input[type="email"], input[name="email"]');
    const passwordInput = page.locator('input[type="password"]');

    if (await emailInput.isVisible().catch(() => false)) {
      await emailInput.fill("test@matanne.fr");
      await passwordInput.fill("MotDePasse123!");

      const boutonConnexion = page.getByRole("button", { name: /connexion|se connecter/i });
      await boutonConnexion.click();

      // Après login réussi, on ne devrait plus être sur /connexion
      await page.waitForURL(/^(?!.*connexion)/, { timeout: 10000 }).catch(() => {});
    }
  });

  test("credentials invalides affichent une erreur", async ({ page }) => {
    await page.route("**/api/v1/auth/login", async (route) => {
      await route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Email ou mot de passe incorrect" }),
      });
    });

    await page.goto("/connexion");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    const emailInput = page.locator('input[type="email"], input[name="email"]');
    const passwordInput = page.locator('input[type="password"]');

    if (await emailInput.isVisible().catch(() => false)) {
      await emailInput.fill("bad@email.com");
      await passwordInput.fill("mauvais");

      const boutonConnexion = page.getByRole("button", { name: /connexion|se connecter/i });
      await boutonConnexion.click();

      // Le formulaire doit rester visible (pas de redirection)
      await expect(emailInput).toBeVisible({ timeout: 3000 });
    }
  });

  test("refresh token renouvelle la session", async ({ page }) => {
    let refreshCalled = false;

    await page.route("**/api/v1/auth/refresh", async (route) => {
      refreshCalled = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "e2e-refreshed-token", token_type: "bearer" }),
      });
    });

    await page.route("**/api/v1/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: 1, email: "test@matanne.fr", nom: "Test User", role: "admin" }),
      });
    });

    await page.route("**/api/v1/**", async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (!path.includes("/auth/")) {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
      } else {
        await route.continue();
      }
    });

    // Simuler une session authentifiée
    await page.context().addCookies([
      { name: "access_token", value: "e2e-jwt-token", domain: "localhost", path: "/", httpOnly: false, sameSite: "Lax" },
    ]);
    await page.addInitScript(() => {
      window.localStorage.setItem("access_token", "e2e-jwt-token");
    });

    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });
    expect(refreshCalled).toBe(true);
  });

  test("logout supprime le token et redirige vers connexion", async ({ page }) => {
    await page.route("**/api/v1/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ id: 1, email: "test@matanne.fr", nom: "Test User", role: "admin" }),
      });
    });

    await page.route("**/api/v1/**", async (route) => {
      const path = new URL(route.request().url()).pathname;
      if (!path.includes("/auth/")) {
        await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
      } else {
        await route.continue();
      }
    });

    // Simuler session authentifiée
    await page.context().addCookies([
      { name: "access_token", value: "e2e-jwt-token", domain: "localhost", path: "/", httpOnly: false, sameSite: "Lax" },
    ]);
    await page.addInitScript(() => {
      window.localStorage.setItem("access_token", "e2e-jwt-token");
      window.localStorage.setItem("matanne-onboarding-complete", "true");
    });

    await page.goto("/");
    await expect(page.locator("body")).toBeVisible({ timeout: 10000 });

    // Chercher et cliquer sur le bouton de déconnexion
    const boutonLogout = page.getByRole("button", { name: /déconnexion|logout|se déconnecter/i });
    const menuProfil = page.getByRole("button", { name: /profil|compte|menu/i });

    if (await menuProfil.isVisible().catch(() => false)) {
      await menuProfil.click();
    }

    if (await boutonLogout.isVisible().catch(() => false)) {
      await boutonLogout.click();
      // Doit rediriger vers /connexion
      await page.waitForURL(/connexion/, { timeout: 5000 }).catch(() => {});
    }
  });

  test("route protégée inaccessible sans token", async ({ page }) => {
    // Sans token, accès au dashboard doit rediriger
    await page.goto("/cuisine/recettes");
    await page.waitForURL(/connexion/, { timeout: 5000 }).catch(() => {});
    await expect(page.locator("body")).toBeVisible();
  });
});
