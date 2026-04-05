// Tests API maison — projets, entretien, jardin, stocks, charges, cellier, artisans

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
  listerProjets,
  obtenirProjet,
  creerProjet,
  modifierProjet,
  supprimerProjet,
  listerTachesEntretien,
  creerTacheEntretien,
  supprimerTacheEntretien,
  listerElementsJardin,
  creerElementJardin,
  supprimerElementJardin,
  listerStocks,
  creerStock,
  supprimerStock,
  listerCharges,
  listerArticlesCellier,
  creerArticleCellier,
  supprimerArticleCellier,
  listerArtisans,
  creerArtisan,
  supprimerArtisan,
  listerDepensesMaison,
  creerDepenseMaison,
  supprimerDepenseMaison,
  listerMeubles,
  creerMeuble,
  supprimerMeuble,
  statsHubMaison,
} from "@/bibliotheque/api/maison";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

// ─── Projets ──────────────────────────────────────────────

describe("listerProjets", () => {
  it("appelle GET /maison/projets", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Cuisine" }] });
    const result = await listerProjets();
    expect(api.get).toHaveBeenCalled();
    expect(result).toHaveLength(1);
  });
});

describe("obtenirProjet", () => {
  it("appelle GET /maison/projets/:id", async () => {
    api.get.mockResolvedValueOnce({ data: { id: 5, nom: "Salle de bain" } });
    const result = await obtenirProjet(5);
    expect(result.nom).toBe("Salle de bain");
  });
});

describe("creerProjet", () => {
  it("appelle POST /maison/projets", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 10, nom: "Jardin" } });
    const result = await creerProjet({ nom: "Jardin" } as never);
    expect(result.id).toBe(10);
  });
});

describe("modifierProjet", () => {
  it("appelle PATCH /maison/projets/:id", async () => {
    api.patch.mockResolvedValueOnce({ data: { id: 5, nom: "Terrasse" } });
    const result = await modifierProjet(5, { nom: "Terrasse" } as never);
    expect(result.nom).toBe("Terrasse");
  });
});

describe("supprimerProjet", () => {
  it("appelle DELETE /maison/projets/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerProjet(5);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Entretien ────────────────────────────────────────────

describe("listerTachesEntretien", () => {
  it("retourne les tâches", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Vidange chaudière" }] });
    const result = await listerTachesEntretien();
    expect(result).toHaveLength(1);
  });
});

describe("creerTacheEntretien", () => {
  it("crée une tâche", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 3, nom: "Détartrage" } });
    const result = await creerTacheEntretien({ nom: "Détartrage" } as never);
    expect(result.id).toBe(3);
  });
});

describe("supprimerTacheEntretien", () => {
  it("supprime la tâche", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerTacheEntretien(3);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Jardin ───────────────────────────────────────────────

describe("listerElementsJardin", () => {
  it("retourne les éléments", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Tomates" }] });
    const result = await listerElementsJardin();
    expect(result).toHaveLength(1);
  });
});

describe("creerElementJardin", () => {
  it("crée un élément", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 2, nom: "Basilic" } });
    const result = await creerElementJardin({ nom: "Basilic" } as never);
    expect(result.id).toBe(2);
  });
});

describe("supprimerElementJardin", () => {
  it("supprime l'élément", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerElementJardin(2);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Stocks ───────────────────────────────────────────────

describe("listerStocks", () => {
  it("retourne les stocks", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Papier" }] });
    const result = await listerStocks();
    expect(result).toHaveLength(1);
  });
});

describe("creerStock", () => {
  it("crée un stock", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 4, nom: "Éponges" } });
    const result = await creerStock({ nom: "Éponges" } as never);
    expect(result.id).toBe(4);
  });
});

describe("supprimerStock", () => {
  it("supprime le stock", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerStock(4);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Charges ──────────────────────────────────────────────

describe("listerCharges", () => {
  it("retourne les charges", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, libelle: "EDF" }] });
    const result = await listerCharges();
    expect(result).toHaveLength(1);
  });
});

// ─── Cellier ──────────────────────────────────────────────

describe("listerArticlesCellier", () => {
  it("retourne les articles", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Vin rouge" }] });
    const result = await listerArticlesCellier();
    expect(result).toHaveLength(1);
  });
});

describe("creerArticleCellier", () => {
  it("crée un article", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 6, nom: "Champagne" } });
    const result = await creerArticleCellier({ nom: "Champagne" } as never);
    expect(result.id).toBe(6);
  });
});

describe("supprimerArticleCellier", () => {
  it("supprime l'article", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerArticleCellier(6);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Artisans ─────────────────────────────────────────────

describe("listerArtisans", () => {
  it("retourne les artisans", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Plombier Pro" }] });
    const result = await listerArtisans();
    expect(result).toHaveLength(1);
  });
});

describe("creerArtisan", () => {
  it("crée un artisan", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 7, nom: "Électricien" } });
    const result = await creerArtisan({ nom: "Électricien" } as never);
    expect(result.id).toBe(7);
  });
});

describe("supprimerArtisan", () => {
  it("supprime l'artisan", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerArtisan(7);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Meubles ──────────────────────────────────────────────

describe("listerMeubles", () => {
  it("retourne les meubles", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Canapé" }] });
    const result = await listerMeubles();
    expect(result).toHaveLength(1);
  });
});

describe("creerMeuble", () => {
  it("crée un meuble", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 8, nom: "Table" } });
    const result = await creerMeuble({ nom: "Table" } as never);
    expect(result.id).toBe(8);
  });
});

describe("supprimerMeuble", () => {
  it("supprime le meuble", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerMeuble(8);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Dépenses ─────────────────────────────────────────────

describe("listerDepensesMaison", () => {
  it("retourne les dépenses", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, montant: 150 }] });
    const result = await listerDepensesMaison();
    expect(result).toHaveLength(1);
  });
});

describe("creerDepenseMaison", () => {
  it("crée une dépense", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 9, montant: 200 } });
    const result = await creerDepenseMaison({ montant: 200 } as never);
    expect(result.id).toBe(9);
  });
});

describe("supprimerDepenseMaison", () => {
  it("supprime la dépense", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerDepenseMaison(9);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Hub Stats ────────────────────────────────────────────

describe("statsHubMaison", () => {
  it("appelle GET /maison/hub/stats", async () => {
    api.get.mockResolvedValueOnce({ data: { projets_actifs: 3, taches_retard: 1 } });
    const result = await statsHubMaison();
    expect(result.projets_actifs).toBe(3);
  });
});
