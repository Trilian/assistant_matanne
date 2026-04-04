import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { TableauMatchsExpert } from "./tableau-matchs-expert";

const matchsMock = [
  {
    id: 1,
    equipe_domicile: "PSG",
    equipe_exterieur: "OM",
    date_match: "2026-04-05T18:00:00Z",
    championnat: "Ligue 1",
    cote_domicile: 1.8,
    cote_nul: 3.2,
    cote_exterieur: 4.1,
    ev: 0.12,
    prediction_ia: "Victoire domicile",
    proba_ia: 0.64,
    confiance_ia: 0.74,
    pattern_detecte: "Value Bet",
    forme_domicile: "VVN",
    forme_exterieur: "NVD",
  },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: { items: matchsMock },
    isLoading: false,
    error: null,
  }),
}));

describe("TableauMatchsExpert", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche une aide mobile pour balayer le tableau", () => {
    render(<TableauMatchsExpert />);

    expect(screen.getByText(/Balayer horizontalement pour voir toutes les colonnes/i)).toBeInTheDocument();
    expect(screen.getByText("PSG")).toBeInTheDocument();
    expect(screen.getByText("OM")).toBeInTheDocument();
  });
});
