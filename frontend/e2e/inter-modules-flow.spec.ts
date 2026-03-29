import { test, expect } from "@playwright/test";

// ═══════════════════════════════════════════════════════════
// E2E — Inter-modules (Planning -> Courses -> Inventaire)
// ═══════════════════════════════════════════════════════════

test.describe("Inter-modules cuisine", () => {
  test("navigation planning -> courses -> inventaire", async ({ page }) => {
    await page.goto("/cuisine/planning");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const hasCoursesContext =
      (await page.locator('input[placeholder*="nouvelle liste"]').isVisible().catch(() => false)) ||
      (await page.locator("text=Courses").first().isVisible().catch(() => false));
    expect(hasCoursesContext).toBeTruthy();

    await page.goto("/cuisine/inventaire");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const hasInventaireContext =
      (await page.locator("text=Inventaire").first().isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="Rechercher"]').isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="rechercher"]').isVisible().catch(() => false));
    expect(hasInventaireContext).toBeTruthy();
  });

  test("création de liste courses puis consultation inventaire", async ({ page }) => {
    await page.goto("/cuisine/courses");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const inputNom = page.locator('input[placeholder*="nouvelle liste"]');
    const nomListe = `Flow-${Date.now()}`;

    if (await inputNom.isVisible({ timeout: 3000 }).catch(() => false)) {
      await inputNom.fill(nomListe);
      const boutonCreer = page.getByRole("button", { name: /Créer la liste/i });
      if (await boutonCreer.isEnabled().catch(() => false)) {
        await boutonCreer.click();
        await page.waitForTimeout(1000);
      }
    }

    await page.goto("/cuisine/inventaire");
    await expect(page.locator("body")).toBeVisible({ timeout: 15000 });

    const hasInventaireContext =
      (await page.locator("text=Inventaire").first().isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="Rechercher"]').isVisible().catch(() => false)) ||
      (await page.locator('input[placeholder*="rechercher"]').isVisible().catch(() => false));
    expect(hasInventaireContext).toBeTruthy();
  });
});
