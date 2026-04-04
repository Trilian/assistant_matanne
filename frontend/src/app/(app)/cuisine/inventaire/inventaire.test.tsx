import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageInventaire from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/inventaire",
}));

let articlesCourants = [
  { id: 1, nom: "Tomates", categorie: "Légumes", quantite: 5, unite: "kg", date_peremption: "2025-02-01" },
  { id: 2, nom: "Lait", categorie: "Laitier", quantite: 2, unite: "L", date_peremption: "2025-01-20" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("alertes")) return { data: [], isLoading: false };
    return { data: articlesCourants, isLoading: false };
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
  beforeEach(() => {
    vi.clearAllMocks();
    articlesCourants = [
      { id: 1, nom: "Tomates", categorie: "Légumes", quantite: 5, unite: "kg", date_peremption: "2025-02-01" },
      { id: 2, nom: "Lait", categorie: "Laitier", quantite: 2, unite: "L", date_peremption: "2025-01-20" },
    ];
  });

  it("affiche le titre Inventaire", () => {
    renderWithQuery(<PageInventaire />);
    expect(screen.getByText(/Inventaire/)).toBeInTheDocument();
  });

  it("affiche les articles en stock et l'aide mobile du tableau", () => {
    renderWithQuery(<PageInventaire />);
    expect(screen.getByText("Tomates")).toBeInTheDocument();
    expect(screen.getByText("Lait")).toBeInTheDocument();
    expect(
      screen.getByText(/Balayer horizontalement pour voir toutes les colonnes/i)
    ).toBeInTheDocument();
  });

  it("affiche les catégories de filtre", () => {
    renderWithQuery(<PageInventaire />);
    expect(screen.getAllByText("Tous").length).toBeGreaterThanOrEqual(1);
  });

  it("affiche un état vide guidé quand l'inventaire est vide", () => {
    articlesCourants = [];
    renderWithQuery(<PageInventaire />);

    expect(screen.getByText(/Aucun article dans/i)).toBeInTheDocument();
    expect(screen.getByText(/Ajoute un premier produit pour suivre ton stock/i)).toBeInTheDocument();
  });
});
