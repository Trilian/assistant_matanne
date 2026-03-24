import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import LotoPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/jeux/loto",
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
    return { data: mockGrilles, isLoading: false };
  }),
}));

vi.mock("@/bibliotheque/api/jeux", () => ({
  listerTirages: vi.fn(),
  listerGrilles: vi.fn(),
}));

describe("LotoPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Loto", () => {
    render(<LotoPage />);
    expect(screen.getByText(/Loto/)).toBeInTheDocument();
  });

  it("affiche la section Derniers tirages", () => {
    render(<LotoPage />);
    expect(screen.getByText("Derniers tirages")).toBeInTheDocument();
  });
});
