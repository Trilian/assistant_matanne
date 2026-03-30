import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import MarcheHabitatPage from "@/app/(app)/habitat/marche/page";

const refetchMock = vi.fn();

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: {
      source: {
        dataset_id: "642205e1f2a0d0428a738699",
        resource_id: "resource-74",
        resource_title: "74 - Haute-Savoie",
      },
      query: {
        departement: "74",
        commune: "Annecy",
        code_postal: "74000",
        type_local: "Maison",
      },
      resume: {
        nb_transactions: 12,
        prix_m2_median: 4650,
        valeur_mediane: 520000,
        surface_mediane: 108,
        dernier_mois: { mois: "2025-12", transactions: 2, prix_m2_median: 4710 },
      },
      historique: [
        { mois: "2025-11", transactions: 3, prix_m2_median: 4620, prix_m2_moyen: 4680 },
        { mois: "2025-12", transactions: 2, prix_m2_median: 4710, prix_m2_moyen: 4750 },
      ],
      repartition_types: [{ type_local: "Maison", transactions: 8, prix_m2_median: 4700 }],
      transactions: [
        {
          date_mutation: "2025-12-05",
          valeur_fonciere: 540000,
          prix_m2: 4800,
          commune: "Annecy",
          type_local: "Maison",
          adresse: "12 rue des Alpes",
        },
      ],
    },
    refetch: refetchMock,
    isFetching: false,
  }),
}));

describe("MarcheHabitatPage", () => {
  it("affiche les indicateurs DVF et les transactions recentes", () => {
    render(<MarcheHabitatPage />);

    expect(screen.getByText(/Marche Habitat/i)).toBeInTheDocument();
    expect(screen.getByText(/Transactions recentes/i)).toBeInTheDocument();
    expect(screen.getByText(/12 rue des Alpes/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Actualiser l'analyse/i })).toBeInTheDocument();
  });
});
