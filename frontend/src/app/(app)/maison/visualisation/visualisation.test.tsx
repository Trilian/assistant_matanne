import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageVisualisation from "./page";

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({ invalidateQueries: vi.fn() }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/visualisation",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("etages")) return { data: [0, 1], isLoading: false };
    return { data: [{ id: 1, nom: "Salon", surface: 25, etage: 0 }], isLoading: false };
  }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerPieces: vi.fn(),
  listerEtages: vi.fn(),
}));

describe("PageVisualisation", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Plan de la maison", () => {
    render(<PageVisualisation />);
    expect(screen.getByText(/Plan de la maison/)).toBeInTheDocument();
  });

  it("affiche la description", () => {
    render(<PageVisualisation />);
    expect(screen.getByText(/Vue interactive/)).toBeInTheDocument();
  });
});
