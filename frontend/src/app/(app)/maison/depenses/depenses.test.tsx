import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageDepenses from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/depenses",
}));

const mockDepenses = [
  { id: 1, libelle: "Peinture", montant: 89.90, categorie: "Travaux", date: "2025-01-15" },
  { id: 2, libelle: "Ampoules LED", montant: 25.00, categorie: "Équipement", date: "2025-01-10" },
];

const mockStats = {
  total_mois: 114.90,
  total_annee: 1200.00,
  moyenne_mensuelle: 100.00,
  delta_mois_precedent: -5,
  par_categorie: { Travaux: 89.90, "Équipement": 25.00 },
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("stats")) return { data: mockStats, isLoading: false };
    return { data: mockDepenses, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerDepensesMaison: vi.fn(),
  creerDepenseMaison: vi.fn(),
  modifierDepenseMaison: vi.fn(),
  supprimerDepenseMaison: vi.fn(),
  statsDepensesMaison: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageDepenses", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Dépenses", () => {
    renderWithQuery(<PageDepenses />);
    expect(screen.getByText(/Dépenses/)).toBeInTheDocument();
  });

  it("affiche les dépenses", () => {
    renderWithQuery(<PageDepenses />);
    expect(screen.getByText("Peinture")).toBeInTheDocument();
    expect(screen.getByText("Ampoules LED")).toBeInTheDocument();
  });
});
