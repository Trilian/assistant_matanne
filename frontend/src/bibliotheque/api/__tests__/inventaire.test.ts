// Tests API inventaire — CRUD + alertes + emplacements

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
  listerInventaire,
  listerEmplacements,
  ajouterArticleInventaire,
  modifierArticleInventaire,
  supprimerArticleInventaire,
  obtenirAlertes,
} from "@/bibliotheque/api/inventaire";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

describe("listerInventaire", () => {
  it("appelle GET /inventaire sans filtre", async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1, nom: "Tomates" }] });

    const result = await listerInventaire();

    expect(api.get).toHaveBeenCalledWith("/inventaire", { params: {} });
    expect(result).toHaveLength(1);
  });

  it("filtre par emplacement", async () => {
    api.get.mockResolvedValueOnce({ data: [] });

    await listerInventaire("frigo");

    expect(api.get).toHaveBeenCalledWith("/inventaire", { params: { emplacement: "frigo" } });
  });
});

describe("listerEmplacements", () => {
  it("retourne la liste des emplacements", async () => {
    api.get.mockResolvedValueOnce({ data: ["frigo", "placard", "cellier"] });

    const result = await listerEmplacements();

    expect(api.get).toHaveBeenCalledWith("/inventaire/emplacements");
    expect(result).toContain("frigo");
  });
});

describe("ajouterArticleInventaire", () => {
  it("appelle POST /inventaire", async () => {
    const dto = { nom: "Beurre", quantite: 2, emplacement: "frigo" };
    api.post.mockResolvedValueOnce({ data: { id: 10, ...dto } });

    const result = await ajouterArticleInventaire(dto as never);

    expect(api.post).toHaveBeenCalledWith("/inventaire", dto);
    expect(result.id).toBe(10);
  });
});

describe("modifierArticleInventaire", () => {
  it("appelle PUT /inventaire/:id", async () => {
    api.put.mockResolvedValueOnce({ data: { id: 5, nom: "Beurre doux", quantite: 3 } });

    const result = await modifierArticleInventaire(5, { quantite: 3 } as never);

    expect(api.put).toHaveBeenCalledWith("/inventaire/5", { quantite: 3 });
    expect(result.quantite).toBe(3);
  });
});

describe("supprimerArticleInventaire", () => {
  it("appelle DELETE /inventaire/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });

    await supprimerArticleInventaire(15);

    expect(api.delete).toHaveBeenCalledWith("/inventaire/15");
  });
});

describe("obtenirAlertes", () => {
  it("appelle GET /inventaire/alertes", async () => {
    const alertes = [{ id: 3, nom: "Yaourt", date_peremption: "2024-01-01" }];
    api.get.mockResolvedValueOnce({ data: alertes });

    const result = await obtenirAlertes();

    expect(api.get).toHaveBeenCalledWith("/inventaire/alertes");
    expect(result).toHaveLength(1);
  });
});
