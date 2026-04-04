import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageActivites from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/activites",
}));

const mockActivites = [
  { id: 1, titre: "Parc", type: "sortie", date: "2025-01-25", lieu: "Lyon", duree: 120 },
  { id: 2, titre: "Piscine", type: "sport", date: "2025-01-26", lieu: "Paris", duree: 60 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockActivites, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerActivites: vi.fn(),
  creerActivite: vi.fn(),
  obtenirSuggestionsActivitesAuto: vi.fn().mockResolvedValue({
    suggestions: "- Sortie vélo\n- Musée des sciences",
    suggestions_struct: [
      { titre: "Sortie vélo", description: "Balade en forêt", type: "sport", duree_minutes: 90, lieu: "Parc" },
      { titre: "Musée des sciences", description: "Exposition interactive", type: "culture", duree_minutes: 120, lieu: "Lyon" },
    ],
  }),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageActivites", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Activités", () => {
    renderWithQuery(<PageActivites />);
    expect(screen.getByRole("heading", { name: /Activit/ })).toBeInTheDocument();
  });

  it("affiche les activités", () => {
    renderWithQuery(<PageActivites />);
    expect(screen.getByText("Parc")).toBeInTheDocument();
    expect(screen.getByText("Piscine")).toBeInTheDocument();
  });

  // Pré-remplissage via suggestions structurées
  it("affiche le bouton Suggestions IA", () => {
    renderWithQuery(<PageActivites />);
    // Le bouton dans l'en-tête qui ouvre le dialogue IA
    expect(screen.getByText(/Suggestions IA/)).toBeInTheDocument();
  });

  it("ouvre le dialogue IA et affiche le bouton Générer", async () => {
    renderWithQuery(<PageActivites />);
    fireEvent.click(screen.getByText(/Suggestions IA/));
    await waitFor(() => {
      expect(screen.getByText(/Générer des suggestions/)).toBeInTheDocument();
    });
  });

  it("appelle obtenirSuggestionsActivitesAuto lors du clic IA", async () => {
    const { obtenirSuggestionsActivitesAuto } = await import("@/bibliotheque/api/famille");
    renderWithQuery(<PageActivites />);
    fireEvent.click(screen.getByText(/Suggestions IA/));
    await waitFor(() => screen.getByText(/Générer des suggestions/));
    fireEvent.click(screen.getByText(/Générer des suggestions/));
    await waitFor(() => {
      expect(obtenirSuggestionsActivitesAuto).toHaveBeenCalled();
    });
  });

  it("affiche les cards de pré-remplissage après réponse IA", async () => {
    renderWithQuery(<PageActivites />);
    fireEvent.click(screen.getByText(/Suggestions IA/));
    await waitFor(() => screen.getByText(/Générer des suggestions/));
    fireEvent.click(screen.getByText(/Générer des suggestions/));
    await waitFor(() => {
      expect(screen.getByText("Sortie vélo")).toBeInTheDocument();
      expect(screen.getByText("Musée des sciences")).toBeInTheDocument();
    });
  });
});
