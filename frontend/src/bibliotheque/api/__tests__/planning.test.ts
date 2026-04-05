// Tests API planning — semaine, mensuel, repas, IA

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
  obtenirPlanningSemaine,
  obtenirPlanningMensuel,
  definirRepas,
  supprimerRepas,
  genererPlanningSemaine,
  obtenirSuggestionsRapides,
} from "@/bibliotheque/api/planning";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

describe("obtenirPlanningSemaine", () => {
  it("appelle GET /planning/semaine sans param", async () => {
    const planning = { jours: [], date_debut: "2024-01-01" };
    api.get.mockResolvedValueOnce({ data: planning });

    const result = await obtenirPlanningSemaine();

    expect(api.get).toHaveBeenCalledWith("/planning/semaine");
    expect(result).toEqual(planning);
  });

  it("passe la date de début en query", async () => {
    api.get.mockResolvedValueOnce({ data: { jours: [] } });

    await obtenirPlanningSemaine("2024-06-10");

    expect(api.get).toHaveBeenCalledWith("/planning/semaine?date_debut=2024-06-10");
  });
});

describe("obtenirPlanningMensuel", () => {
  it("appelle GET /planning/mensuel avec mois", async () => {
    api.get.mockResolvedValueOnce({ data: { semaines: [] } });

    await obtenirPlanningMensuel("2024-06");

    expect(api.get).toHaveBeenCalledWith("/planning/mensuel?mois=2024-06");
  });
});

describe("definirRepas", () => {
  it("appelle POST /planning/repas", async () => {
    const dto = { date: "2024-06-10", type_repas: "diner", recette_id: 5 };
    const repas = { id: 1, ...dto };
    api.post.mockResolvedValueOnce({ data: repas });

    const result = await definirRepas(dto as never);

    expect(api.post).toHaveBeenCalledWith("/planning/repas", dto);
    expect(result.id).toBe(1);
  });
});

describe("supprimerRepas", () => {
  it("appelle DELETE /planning/repas/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });

    await supprimerRepas(42);

    expect(api.delete).toHaveBeenCalledWith("/planning/repas/42");
  });
});

describe("genererPlanningSemaine", () => {
  it("appelle POST /planning/generer", async () => {
    const planning = { jours: [{ date: "2024-06-10", repas: [] }] };
    api.post.mockResolvedValueOnce({ data: planning });

    const result = await genererPlanningSemaine({ contraintes: "rapide" } as never);

    expect(api.post).toHaveBeenCalledWith("/planning/generer", { contraintes: "rapide" });
    expect(result.jours).toHaveLength(1);
  });
});

describe("obtenirSuggestionsRapides", () => {
  it("appelle GET /planning/suggestions-rapides et retourne suggestions", async () => {
    api.get.mockResolvedValueOnce({
      data: { suggestions: [{ id: 1, nom: "Pasta", score: 0.9 }] },
    });

    const result = await obtenirSuggestionsRapides("diner", 3);

    expect(api.get).toHaveBeenCalledWith(
      "/planning/suggestions-rapides?type_repas=diner&nombre=3"
    );
    expect(result).toHaveLength(1);
  });
});
