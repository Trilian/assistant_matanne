import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageInventaire from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/inventaire",
}));

const mockArticles = [
  { id: 1, nom: "Tomates", categorie: "Légumes", quantite: 5, unite: "kg", date_peremption: "2025-02-01" },
  { id: 2, nom: "Lait", categorie: "Laitier", quantite: 2, unite: "L", date_peremption: "2025-01-20" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("alertes")) return { data: [], isLoading: false };
    return { data: mockArticles, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/inventaire", () => ({
  listerInventaire: vi.fn(),
  ajouterArticleInventaire: vi.fn(),
  supprimerArticleInventaire: vi.fn(),
  obtenirAlertes: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageInventaire", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Inventaire", () => {
    renderWithQuery(<PageInventaire />);
    expect(screen.getByText(/Inventaire/)).toBeInTheDocument();
  });

  it("affiche les articles en stock", () => {
    renderWithQuery(<PageInventaire />);
    expect(screen.getByText("Tomates")).toBeInTheDocument();
    expect(screen.getByText("Lait")).toBeInTheDocument();
  });

  it("affiche les catégories de filtre", () => {
    renderWithQuery(<PageInventaire />);
    expect(screen.getAllByText("Tous").length).toBeGreaterThanOrEqual(1);
  });
});
