import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageEntretien from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/entretien",
}));

const mockTaches = [
  { id: 1, nom: "Nettoyer four", categorie: "cuisine", piece: "Cuisine", fait: false, frequence_jours: 30 },
  { id: 2, nom: "Aspirateur salon", categorie: "menage", piece: "Salon", fait: true, frequence_jours: 7 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("sante")) return { data: { score_global: 85, zones: [], actions_urgentes: [] }, isLoading: false };
    return { data: mockTaches, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerTachesEntretien: vi.fn(),
  obtenirSanteAppareils: vi.fn(),
  creerTacheEntretien: vi.fn(),
  supprimerTacheEntretien: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageEntretien", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Entretien", () => {
    renderWithQuery(<PageEntretien />);
    expect(screen.getByText(/Entretien/)).toBeInTheDocument();
  });

  it("affiche les tâches d'entretien", () => {
    renderWithQuery(<PageEntretien />);
    expect(screen.getByText("Nettoyer four")).toBeInTheDocument();
    expect(screen.getByText("Aspirateur salon")).toBeInTheDocument();
  });
});
