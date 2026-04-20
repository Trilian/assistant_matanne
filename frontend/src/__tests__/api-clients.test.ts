// ═══════════════════════════════════════════════════════════
// Tests API clients — preferences, push, calendriers
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock axios-based clientApi
vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  obtenirPreferences,
  sauvegarderPreferences,
  modifierPreferences,
} from "@/bibliotheque/api/preferences";
import {
  souscrirePush,
  desabonnerPush,
  statutPush,
} from "@/bibliotheque/api/push";
import {
  listerCalendriers,
  listerEvenements,
  evenementsAujourdHui,
  synchroniserGoogle,
} from "@/bibliotheque/api/calendriers";

const mockedApi = vi.mocked(clientApi);

beforeEach(() => {
  vi.clearAllMocks();
});

// ─── Preferences ──────────────────────────────────────────

describe("API Preferences", () => {
  const mockPrefs = {
    user_id: "abc",
    nb_adultes: 2,
    jules_present: true,
    jules_age_mois: 24,
    temps_semaine: 30,
    temps_weekend: 60,
    aliments_exclus: ["coriandre"],
    aliments_favoris: ["pâtes"],
    poisson_par_semaine: 2,
    nb_poisson_blanc: 1,
    nb_poisson_gras: 1,
    vegetarien_par_semaine: 1,
    viande_rouge_max: 2,
    robots: ["Thermomix"],
    magasins_preferes: ["Leclerc"],
    objectif_calories: 2000,
    objectif_proteines: 60,
    objectif_lipides: 70,
    objectif_glucides: 260,
  };

  it("obtenirPreferences appelle GET /preferences", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: mockPrefs });

    const result = await obtenirPreferences();

    expect(mockedApi.get).toHaveBeenCalledWith("/preferences");
    expect(result).toEqual(mockPrefs);
  });

  it("sauvegarderPreferences appelle PUT /preferences", async () => {
    mockedApi.put.mockResolvedValueOnce({ data: mockPrefs });

    const result = await sauvegarderPreferences(mockPrefs);

    expect(mockedApi.put).toHaveBeenCalledWith("/preferences", mockPrefs);
    expect(result).toEqual(mockPrefs);
  });

  it("modifierPreferences appelle PATCH /preferences", async () => {
    const patch = { nb_adultes: 3 };
    mockedApi.patch.mockResolvedValueOnce({ data: { ...mockPrefs, ...patch } });

    const result = await modifierPreferences(patch);

    expect(mockedApi.patch).toHaveBeenCalledWith("/preferences", patch);
    expect(result.nb_adultes).toBe(3);
  });
});

// ─── Push ─────────────────────────────────────────────────

describe("API Push", () => {
  it("souscrirePush appelle POST /push/subscribe", async () => {
    const payload = {
      endpoint: "https://push.example.com/abc",
      keys: { p256dh: "key1", auth: "key2" },
    };
    mockedApi.post.mockResolvedValueOnce({
      data: { success: true, message: "ok" },
    });

    const result = await souscrirePush(payload);

    expect(mockedApi.post).toHaveBeenCalledWith("/push/subscribe", payload);
    expect(result.success).toBe(true);
  });

  it("desabonnerPush appelle DELETE /push/unsubscribe", async () => {
    mockedApi.delete.mockResolvedValueOnce({
      data: { success: true, message: "ok" },
    });

    const result = await desabonnerPush("https://push.example.com/abc");

    expect(mockedApi.delete).toHaveBeenCalledWith("/push/unsubscribe", {
      data: { endpoint: "https://push.example.com/abc" },
    });
    expect(result.success).toBe(true);
  });

  it("statutPush appelle GET /push/status", async () => {
    const mockStatus = {
      has_subscriptions: true,
      subscription_count: 2,
      notifications_enabled: true,
    };
    mockedApi.get.mockResolvedValueOnce({ data: mockStatus });

    const result = await statutPush();

    expect(mockedApi.get).toHaveBeenCalledWith("/push/status");
    expect(result.has_subscriptions).toBe(true);
  });
});

// ─── Calendriers ──────────────────────────────────────────

describe("API Calendriers", () => {
  it("listerCalendriers appelle GET /calendriers", async () => {
    const mock = [{ id: 1, nom: "Google", provider: "google" }];
    mockedApi.get.mockResolvedValueOnce({ data: mock });

    const result = await listerCalendriers();

    expect(mockedApi.get).toHaveBeenCalledWith("/calendriers");
    expect(result).toHaveLength(1);
  });

  it("listerEvenements appelle GET /calendriers/evenements", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: [] });

    const result = await listerEvenements({ date_debut: "2025-01-01", date_fin: "2025-01-31" });

    expect(mockedApi.get).toHaveBeenCalledWith(
      "/calendriers/evenements?date_debut=2025-01-01&date_fin=2025-01-31"
    );
    expect(result).toEqual([]);
  });

  it("listerEvenements inclut les filtres avancés (calendrier_id)", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: { items: [] } });

    await listerEvenements({ calendrier_id: 7, date_debut: "2026-04-01", date_fin: "2026-04-08" });

    expect(mockedApi.get).toHaveBeenCalledWith(
      "/calendriers/evenements?calendrier_id=7&date_debut=2026-04-01&date_fin=2026-04-08"
    );
  });

  it("listerCalendriers accepte le filtre provider", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: { items: [] } });

    await listerCalendriers("ical_url");

    expect(mockedApi.get).toHaveBeenCalledWith("/calendriers?provider=ical_url");
  });

  it("propage les erreurs réseau sur synchroniserGoogle", async () => {
    const erreur = new Error("network");
    mockedApi.post.mockRejectedValueOnce(erreur);

    await expect(synchroniserGoogle()).rejects.toThrow("network");
  });

  it("evenementsAujourdHui appelle GET /calendriers/evenements/aujourd-hui", async () => {
    const mock = [{ id: 1, titre: "RDV dentiste" }];
    mockedApi.get.mockResolvedValueOnce({ data: mock });

    const result = await evenementsAujourdHui();

    expect(mockedApi.get).toHaveBeenCalledWith(
      "/calendriers/evenements/aujourd-hui"
    );
    expect(result).toHaveLength(1);
  });
});
