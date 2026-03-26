import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import EuromillionsPage from "@/app/(app)/jeux/euromillions/page";

vi.mock("next/navigation", () => ({
  useSearchParams: () => ({
    get: (k: string) => {
      if (k === "numeros") return "1,2,3,4,5";
      if (k === "etoiles") return "1,2";
      return null;
    },
  }),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("tirages")) return { data: [], isLoading: false };
    if (key.includes("grilles")) return { data: [], isLoading: false };
    if (key.includes("stats")) {
      return {
        data: {
          total_tirages: 0,
          frequences_numeros: {},
          frequences_etoiles: {},
          numeros_chauds: [],
          numeros_froids: [],
          numeros_retard: [],
          etoiles_chaudes: [],
          etoiles_froides: [],
        },
        isLoading: false,
      };
    }
    if (key.includes("retard")) return { data: [], isLoading: false };
    if (key.includes("backtest")) return { data: undefined, isLoading: false };
    return { data: undefined, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/composants/jeux/heatmap-numeros", () => ({
  HeatmapNumeros: () => <div>heatmap</div>,
}));

vi.mock("@/composants/jeux/generateur-grille", () => ({
  GenerateurGrille: () => <div>generateur</div>,
}));

vi.mock("@/composants/jeux/backtest-resultat", () => ({
  BacktestResultatCard: () => <div>backtest-card</div>,
}));

vi.mock("@/composants/jeux/backtest-euromillions-vue", () => ({
  BacktestEuromillionsVue: () => <div>backtest-vue</div>,
}));

describe("EuromillionsPage", () => {
  it("affiche le pré-remplissage OCR quand query params présents", () => {
    render(<EuromillionsPage />);

    expect(screen.getByText(/Euromillions/i)).toBeInTheDocument();
    expect(screen.getByText(/Pré-remplissage depuis OCR ticket/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Enregistrer cette grille/i })).toBeInTheDocument();
  });
});
