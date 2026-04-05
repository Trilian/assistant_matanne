// Tests API jeux — paris, loto, euromillions, performance

import { describe, it, expect, vi, beforeEach } from "vitest";

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
  obtenirDashboardJeux,
  listerMatchs,
  listerParis,
  creerPari,
  modifierPari,
  supprimerPari,
  obtenirStatsParis,
  obtenirPredictionMatch,
  obtenirValueBets,
  listerTirages,
  listerGrilles,
  obtenirStatsLoto,
  obtenirNumerosRetard,
  genererGrilleLoto,
  obtenirTiragesEuromillions,
  obtenirGrillesEuromillions,
  obtenirStatsEuromillions,
  genererGrilleEuromillions,
  obtenirPerformance,
  obtenirAnalyseIA,
} from "@/bibliotheque/api/jeux";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

// ─── Dashboard ────────────────────────────────────────────

describe("obtenirDashboardJeux", () => {
  it("appelle GET /jeux/dashboard", async () => {
    api.get.mockResolvedValueOnce({ data: { total_paris: 10, benefice: 50 } });
    const result = await obtenirDashboardJeux();
    expect(result.total_paris).toBe(10);
  });
});

// ─── Matchs ───────────────────────────────────────────────

describe("listerMatchs", () => {
  it("retourne les matchs", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, equipe_dom: "PSG" }] });
    const result = await listerMatchs();
    expect(result).toHaveLength(1);
  });
});

// ─── Paris sportifs ───────────────────────────────────────

describe("listerParis", () => {
  it("retourne les paris", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, mise: 10 }] });
    const result = await listerParis();
    expect(result).toHaveLength(1);
  });
});

describe("creerPari", () => {
  it("crée un pari", async () => {
    const pari = { match_id: 1, mise: 10, cote: 2.5, pronostic: "1" };
    api.post.mockResolvedValueOnce({ data: { id: 5, ...pari, statut: "en_cours" } });
    const result = await creerPari(pari as never);
    expect(result.id).toBe(5);
    expect(result.statut).toBe("en_cours");
  });
});

describe("modifierPari", () => {
  it("modifie un pari", async () => {
    api.patch.mockResolvedValueOnce({ data: { id: 5, mise: 20 } });
    const result = await modifierPari(5, { mise: 20 });
    expect(result.mise).toBe(20);
  });
});

describe("supprimerPari", () => {
  it("supprime le pari", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerPari(5);
    expect(api.delete).toHaveBeenCalled();
  });
});

describe("obtenirStatsParis", () => {
  it("retourne les stats", async () => {
    api.get.mockResolvedValueOnce({ data: { total: 100, gagne: 60, benefice: 200 } });
    const result = await obtenirStatsParis();
    expect(result.benefice).toBe(200);
  });
});

// ─── Prédictions ──────────────────────────────────────────

describe("obtenirPredictionMatch", () => {
  it("retourne la prédiction", async () => {
    api.get.mockResolvedValueOnce({ data: { match_id: 1, prediction: "1", confiance: 0.85 } });
    const result = await obtenirPredictionMatch(1);
    expect(result.confiance).toBe(0.85);
  });
});

describe("obtenirValueBets", () => {
  it("retourne les value bets", async () => {
    api.get.mockResolvedValueOnce({ data: [{ match_id: 1, ev: 8.5 }] });
    const result = await obtenirValueBets(5.0);
    expect(result).toHaveLength(1);
  });
});

// ─── Loto ─────────────────────────────────────────────────

describe("listerTirages", () => {
  it("retourne les tirages", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, numeros: [1, 2, 3, 4, 5] }] });
    const result = await listerTirages();
    expect(result).toHaveLength(1);
  });
});

describe("listerGrilles", () => {
  it("retourne les grilles", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, numeros: [7, 14, 21] }] });
    const result = await listerGrilles();
    expect(result).toHaveLength(1);
  });
});

describe("obtenirStatsLoto", () => {
  it("retourne les stats loto", async () => {
    api.get.mockResolvedValueOnce({ data: { total_tirages: 50, numeros_chauds: [7, 14] } });
    const result = await obtenirStatsLoto();
    expect(result.total_tirages).toBe(50);
  });
});

describe("obtenirNumerosRetard", () => {
  it("retourne les numéros en retard", async () => {
    api.get.mockResolvedValueOnce({ data: [{ numero: 33, retard: 15 }] });
    const result = await obtenirNumerosRetard();
    expect(result[0].numero).toBe(33);
  });
});

describe("genererGrilleLoto", () => {
  it("génère une grille loto", async () => {
    api.post.mockResolvedValueOnce({ data: { numeros: [1, 5, 12, 33, 44], numero_chance: 7 } });
    const result = await genererGrilleLoto("statistique");
    expect(result.numeros).toHaveLength(5);
  });
});

// ─── Euromillions ─────────────────────────────────────────

describe("obtenirTiragesEuromillions", () => {
  it("retourne les tirages", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, numeros: [5, 10, 15, 20, 25], etoiles: [3, 7] }] });
    const result = await obtenirTiragesEuromillions();
    expect(result).toHaveLength(1);
  });
});

describe("obtenirGrillesEuromillions", () => {
  it("retourne les grilles", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1 }] });
    const result = await obtenirGrillesEuromillions();
    expect(result).toHaveLength(1);
  });
});

describe("obtenirStatsEuromillions", () => {
  it("retourne les stats", async () => {
    api.get.mockResolvedValueOnce({ data: { total_tirages: 30 } });
    const result = await obtenirStatsEuromillions();
    expect(result.total_tirages).toBe(30);
  });
});

describe("genererGrilleEuromillions", () => {
  it("génère une grille", async () => {
    api.post.mockResolvedValueOnce({ data: { numeros: [1, 10, 20, 30, 40], etoiles: [2, 8] } });
    const result = await genererGrilleEuromillions("ia");
    expect(result.numeros).toHaveLength(5);
  });
});

// ─── Performance ──────────────────────────────────────────

describe("obtenirPerformance", () => {
  it("retourne les métriques performance", async () => {
    api.get.mockResolvedValueOnce({ data: { roi: 15.5, total_mise: 500 } });
    const result = await obtenirPerformance();
    expect(result.roi).toBe(15.5);
  });
});

// ─── Analyse IA ───────────────────────────────────────────

describe("obtenirAnalyseIA", () => {
  it("retourne l'analyse IA pour paris", async () => {
    api.post.mockResolvedValueOnce({ data: { analyse: "Bonne tendance", type: "paris" } });
    const result = await obtenirAnalyseIA("paris");
    expect(result.type).toBe("paris");
  });
});
