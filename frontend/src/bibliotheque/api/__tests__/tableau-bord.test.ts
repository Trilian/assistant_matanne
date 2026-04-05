// Tests API tableau-bord — dashboard, cuisine, bilan, config, alertes

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
  obtenirTableauBord,
  obtenirDashboardCuisine,
  obtenirBilanMensuel,
  obtenirConfigDashboard,
} from "@/bibliotheque/api/tableau-bord";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

describe("obtenirTableauBord", () => {
  it("appelle GET /dashboard", async () => {
    const dashboard = {
      repas_aujourd_hui: [{ type_repas: "diner", recette_nom: "Pasta" }],
      alertes_inventaire: 2,
      articles_courses_restants: 5,
      activites_semaine: 3,
      taches_entretien_urgentes: 1,
    };
    api.get.mockResolvedValueOnce({ data: dashboard });

    const result = await obtenirTableauBord();

    expect(api.get).toHaveBeenCalledWith("/dashboard");
    expect(result.alertes_inventaire).toBe(2);
    expect(result.repas_aujourd_hui).toHaveLength(1);
  });
});

describe("obtenirDashboardCuisine", () => {
  it("appelle GET /dashboard/cuisine", async () => {
    const data = {
      repas_aujourd_hui: [],
      repas_semaine_count: 10,
      nb_recettes: 50,
      articles_courses_restants: 3,
      alertes_inventaire: 0,
      score_anti_gaspillage: 85,
      repas_jules_aujourd_hui: [],
      batch_en_cours: false,
      batch_session_id: null,
    };
    api.get.mockResolvedValueOnce({ data });

    const result = await obtenirDashboardCuisine();

    expect(api.get).toHaveBeenCalledWith("/dashboard/cuisine");
    expect(result.nb_recettes).toBe(50);
    expect(result.score_anti_gaspillage).toBe(85);
  });
});

describe("obtenirBilanMensuel", () => {
  it("appelle GET /dashboard/bilan-mensuel sans paramètre", async () => {
    const bilan = { mois: "2024-06", donnees: {}, synthese_ia: "Bon mois" };
    api.get.mockResolvedValueOnce({ data: bilan });

    const result = await obtenirBilanMensuel();

    expect(api.get).toHaveBeenCalledWith("/dashboard/bilan-mensuel");
    expect(result.synthese_ia).toBe("Bon mois");
  });

  it("passe le mois en paramètre", async () => {
    api.get.mockResolvedValueOnce({ data: { mois: "2024-01" } });

    await obtenirBilanMensuel("2024-01");

    expect(api.get).toHaveBeenCalledWith("/dashboard/bilan-mensuel?mois=2024-01");
  });
});

describe("obtenirConfigDashboard", () => {
  it("appelle GET /dashboard/config", async () => {
    const config = { config_dashboard: { cuisine: true, maison: true, jeux: false } };
    api.get.mockResolvedValueOnce({ data: config });

    const result = await obtenirConfigDashboard();

    expect(api.get).toHaveBeenCalledWith("/dashboard/config");
    expect(result.config_dashboard.cuisine).toBe(true);
  });
});
