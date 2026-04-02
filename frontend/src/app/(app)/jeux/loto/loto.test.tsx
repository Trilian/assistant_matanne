import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import LotoPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/jeux/loto",
  useSearchParams: () => ({ get: vi.fn().mockReturnValue(null) }),
}));

const mockTirages = [
  { id: 1, numeros: [5, 12, 23, 34, 45], numero_chance: 3, date: "2025-01-22" },
];

const mockGrilles = [
  { id: 1, numeros: [5, 12, 23, 34, 45], numero_chance: 3, date: "2025-01-22", gains: 0 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("tirages")) return { data: mockTirages, isLoading: false };
    if (key.includes("stats")) return { data: null, isLoading: false };
    if (key.includes("retard")) return { data: [], isLoading: false };
    if (key.includes("backtest")) return { data: null, isLoading: false };
    return { data: mockGrilles, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), mutateAsync: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ user: null }),
}));

vi.mock("@/bibliotheque/api/jeux", () => ({
  listerTirages: vi.fn(),
  listerGrilles: vi.fn(),
  obtenirStatsLoto: vi.fn(),
  obtenirNumerosRetard: vi.fn(),
  genererGrilleLoto: vi.fn(),
  obtenirBacktest: vi.fn(),
  genererGrilleIAPonderee: vi.fn(),
  analyserGrilleJoueur: vi.fn(),
}));

describe("LotoPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Loto", () => {
    render(<LotoPage />);
    expect(screen.getByRole("heading", { level: 1, name: /Loto/ })).toBeInTheDocument();
  });

  it("affiche la section Fréquences des numéros", () => {
    render(<LotoPage />);
    expect(screen.getByText("Fréquences des numéros")).toBeInTheDocument();
  });
});
