import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageProjets from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/projets",
}));

const mockProjets = [
  { id: 1, nom: "Repeindre salon", statut: "en_cours", priorite: "haute", budget: 500 },
  { id: 2, nom: "Installer étagères", statut: "a_faire", priorite: "basse", budget: 100 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockProjets, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerProjets: vi.fn(),
  creerProjet: vi.fn(),
  supprimerProjet: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageProjets", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Projets", () => {
    renderWithQuery(<PageProjets />);
    expect(screen.getByText(/Projets/)).toBeInTheDocument();
  });

  it("affiche les projets", () => {
    renderWithQuery(<PageProjets />);
    expect(screen.getByText("Repeindre salon")).toBeInTheDocument();
    expect(screen.getByText("Installer étagères")).toBeInTheDocument();
  });
});
