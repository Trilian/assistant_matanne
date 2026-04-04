import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageAchats from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/achats",
}));

const mockAchats = [
  { id: 1, nom: "Livre d'éveil", categorie: "livre", priorite: "haute", achete: false, suggere_par: null },
  { id: 2, nom: "Vélo enfant", categorie: "jouet", priorite: "moyenne", achete: false, suggere_par: "ia" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockAchats, isLoading: false, refetch: vi.fn() }),
  utiliserMutation: () => ({ mutateAsync: vi.fn().mockResolvedValue({}), isPending: false }),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerAchats: vi.fn().mockResolvedValue([
    { id: 1, nom: "Livre d'éveil", categorie: "livre", priorite: "haute", achete: false, suggere_par: null },
    { id: 2, nom: "Vélo enfant", categorie: "jouet", priorite: "moyenne", achete: false, suggere_par: "ia" },
  ]),
  creerAchat: vi.fn().mockResolvedValue({}),
  marquerAchatAchete: vi.fn().mockResolvedValue({}),
  marquerAchatVendu: vi.fn(),
  supprimerAchat: vi.fn().mockResolvedValue({}),
  obtenirSuggestionsAchatsEnrichies: vi.fn().mockResolvedValue({
    items: [
      { titre: "Jouet d'anniversaire", description: "Anniversaire dans 7 jours", source: "anniversaire", fourchette_prix: "20-50€", ou_acheter: "Amazon", pertinence: "haute" },
      { titre: "Vêtement saison", description: "Automne approche", source: "saison", fourchette_prix: "15-30€", ou_acheter: null, pertinence: "moyenne" },
    ],
    total: 2,
  }),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageAchats", () => {
  beforeEach(() => vi.clearAllMocks());

  const ouvrirSuggestionsIA = () => {
    fireEvent.click(screen.getByText("Suggestions IA contextuelles"));
    fireEvent.click(screen.getByRole("button", { name: "Anniversaire" }));
  };

  it("affiche le titre Achats Famille", () => {
    renderWithQuery(<PageAchats />);
    expect(screen.getByText(/Achats Famille/)).toBeInTheDocument();
  });

  it("affiche la section Suggestions IA", () => {
    renderWithQuery(<PageAchats />);
    expect(screen.getByText("Suggestions IA contextuelles")).toBeInTheDocument();
  });

  it("affiche les triggers de suggestions IA", () => {
    renderWithQuery(<PageAchats />);
    fireEvent.click(screen.getByText("Suggestions IA contextuelles"));
    expect(screen.getByRole("button", { name: "Anniversaire" })).toBeInTheDocument();
  });

  it("appelle obtenirSuggestionsAchatsEnrichies lors du clic", async () => {
    const { obtenirSuggestionsAchatsEnrichies } = await import("@/bibliotheque/api/famille");
    renderWithQuery(<PageAchats />);
    ouvrirSuggestionsIA();
    await waitFor(() => {
      expect(obtenirSuggestionsAchatsEnrichies).toHaveBeenCalled();
    });
  });

  it("affiche les suggestions IA après génération", async () => {
    renderWithQuery(<PageAchats />);
    ouvrirSuggestionsIA();
    await waitFor(() => {
      expect(screen.getByText("Jouet d'anniversaire")).toBeInTheDocument();
      expect(screen.getByText("Vêtement saison")).toBeInTheDocument();
    });
  });

  it("affiche les badges source anniversaire et saison", async () => {
    renderWithQuery(<PageAchats />);
    ouvrirSuggestionsIA();
    await waitFor(() => {
      expect(screen.getByText("anniversaire")).toBeInTheDocument();
      expect(screen.getByText("saison")).toBeInTheDocument();
    });
  });

  it("affiche la fourchette de prix dans les suggestions", async () => {
    renderWithQuery(<PageAchats />);
    ouvrirSuggestionsIA();
    await waitFor(() => {
      expect(screen.getByText("20-50€")).toBeInTheDocument();
    });
  });

  it("affiche deux boutons Ajouter pour les suggestions", async () => {
    renderWithQuery(<PageAchats />);
    ouvrirSuggestionsIA();
    await waitFor(() => {
      const addBtns = screen.getAllByText("Ajouter");
      expect(addBtns.length).toBeGreaterThanOrEqual(2);
    });
  });

  it("affiche le bouton Ajouter un achat", () => {
    renderWithQuery(<PageAchats />);
    expect(screen.getByRole("button", { name: "Ajouter" })).toBeInTheDocument();
  });
});
