// Tests API courses — listes et articles

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
  listerListesCourses,
  obtenirListeCourses,
  creerListeCourses,
} from "@/bibliotheque/api/courses";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

describe("listerListesCourses", () => {
  it("transforme la réponse API en modèle frontend", async () => {
    api.get.mockResolvedValueOnce({
      data: {
        items: [
          { id: 1, nom: "Courses semaine", etat: "brouillon", items_count: 3, created_at: "2024-01-01" },
        ],
      },
    });

    const result = await listerListesCourses();

    expect(api.get).toHaveBeenCalledWith("/courses");
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      id: 1,
      nom: "Courses semaine",
      nombre_articles: 3,
    });
  });

  it("gère une réponse vide", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [] } });

    const result = await listerListesCourses();

    expect(result).toEqual([]);
  });
});

describe("obtenirListeCourses", () => {
  it("transforme le détail avec articles", async () => {
    api.get.mockResolvedValueOnce({
      data: {
        id: 10,
        nom: "Ma liste",
        etat: "active",
        items: [
          { id: 1, nom: "Tomates", quantite: 3, coche: false, categorie: "Fruits" },
          { id: 2, nom: "Pain", quantite: 1, coche: true, categorie: "Boulangerie" },
        ],
      },
    });

    const result = await obtenirListeCourses(10);

    expect(api.get).toHaveBeenCalledWith("/courses/10");
    expect(result.nombre_articles).toBe(2);
    expect(result.nombre_coche).toBe(1);
    expect(result.articles[0].est_coche).toBe(false);
    expect(result.articles[1].est_coche).toBe(true);
  });
});

describe("creerListeCourses", () => {
  it("crée et retourne le détail", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 99 } });
    api.get.mockResolvedValueOnce({
      data: { id: 99, nom: "Nouvelle", items: [] },
    });

    const result = await creerListeCourses("Nouvelle");

    expect(api.post).toHaveBeenCalledWith("/courses", { nom: "Nouvelle" });
    expect(result.id).toBe(99);
  });
});
