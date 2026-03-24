import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageStocks from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/stocks",
}));

const mockStocks = [
  { id: 1, nom: "Papier toilette", quantite: 12, seuil: 6, en_alerte: false },
  { id: 2, nom: "Lessive", quantite: 1, seuil: 3, en_alerte: true },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockStocks, isLoading: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerStocks: vi.fn(),
}));

describe("PageStocks", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Stocks", () => {
    render(<PageStocks />);
    expect(screen.getByRole("heading", { name: /Stocks/ })).toBeInTheDocument();
  });

  it("affiche les articles en stock", () => {
    render(<PageStocks />);
    expect(screen.getByText("Papier toilette")).toBeInTheDocument();
    expect(screen.getByText("Lessive")).toBeInTheDocument();
  });

  it("affiche l'alerte stock bas", () => {
    render(<PageStocks />);
    expect(screen.getByText(/stock\(s\) bas/)).toBeInTheDocument();
  });
});
