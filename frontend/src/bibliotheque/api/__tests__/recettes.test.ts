// Tests API recettes — CRUD + suggestions + saison

import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  listerRecettes,
  obtenirRecette,
  creerRecette,
  modifierRecette,
  supprimerRecette,
  obtenirSuggestions,
  listerRecettesSaisonnieres,
} from "@/bibliotheque/api/recettes";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

describe("listerRecettes", () => {
  it("appelle GET /recettes avec pagination", async () => {
    const page = { items: [], total: 0, page: 1, page_size: 20, pages_totales: 0 };
    api.get.mockResolvedValueOnce({ data: page });

    const result = await listerRecettes(2, 10);

    expect(api.get).toHaveBeenCalledOnce();
    expect(api.get.mock.calls[0][0]).toContain("/recettes");
    expect(api.get.mock.calls[0][0]).toContain("page=2");
    expect(result).toEqual(page);
  });

  it("inclut la recherche si fournie", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [] } });

    await listerRecettes(1, 20, "tarte");

    expect(api.get.mock.calls[0][0]).toContain("recherche=tarte");
  });
});

describe("obtenirRecette", () => {
  it("appelle GET /recettes/:id", async () => {
    const recette = { id: 42, nom: "Tarte aux pommes" };
    api.get.mockResolvedValueOnce({ data: recette });

    const result = await obtenirRecette(42);

    expect(api.get).toHaveBeenCalledWith("/recettes/42");
    expect(result).toEqual(recette);
  });
});

describe("creerRecette", () => {
  it("appelle POST /recettes", async () => {
    const dto = { nom: "Quiche", type_repas: "diner" };
    const created = { id: 1, ...dto };
    api.post.mockResolvedValueOnce({ data: created });

    const result = await creerRecette(dto as never);

    expect(api.post).toHaveBeenCalledWith("/recettes", dto);
    expect(result.id).toBe(1);
  });
});

describe("modifierRecette", () => {
  it("appelle PUT /recettes/:id", async () => {
    const dto = { nom: "Quiche lorraine" };
    const updated = { id: 5, nom: "Quiche lorraine" };
    api.put.mockResolvedValueOnce({ data: updated });

    const result = await modifierRecette(5, dto);

    expect(api.put).toHaveBeenCalledWith("/recettes/5", dto);
    expect(result.nom).toBe("Quiche lorraine");
  });
});

describe("supprimerRecette", () => {
  it("appelle DELETE /recettes/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });

    await supprimerRecette(7);

    expect(api.delete).toHaveBeenCalledWith("/recettes/7");
  });
});

describe("obtenirSuggestions", () => {
  it("appelle POST /suggestions/recettes", async () => {
    const suggestions = [{ id: 1, nom: "Pasta" }];
    api.post.mockResolvedValueOnce({ data: suggestions });

    const result = await obtenirSuggestions("rapide");

    expect(api.post).toHaveBeenCalledWith("/suggestions/recettes", { contexte: "rapide" });
    expect(result).toHaveLength(1);
  });
});

describe("listerRecettesSaisonnieres", () => {
  it("appelle GET /recettes/saisonnieres", async () => {
    const resp = { items: [], total: 0, page: 1, page_size: 20, pages_totales: 0, mois: 6, produits_saison: ["tomate"] };
    api.get.mockResolvedValueOnce({ data: resp });

    const result = await listerRecettesSaisonnieres(1, 6);

    expect(api.get).toHaveBeenCalledWith("/recettes/saisonnieres", { params: { page: 1, mois: 6 } });
    expect(result.mois).toBe(6);
  });
});
