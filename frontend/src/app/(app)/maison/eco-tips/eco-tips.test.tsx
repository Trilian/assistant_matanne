import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageEcoTips from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/eco-tips",
}));

const mockActions = [
  { id: 1, titre: "Compostage", description: "Composter les déchets verts", categorie: "Déchets", impact: "Fort", economie_estimee: 50, actif: true },
  { id: 2, titre: "LED partout", description: "Remplacer ampoules", categorie: "Énergie", impact: "Moyen", economie_estimee: 30, actif: true },
  { id: 3, titre: "Récupérateur eau", description: "Eau de pluie", categorie: "Eau", impact: "Fort", economie_estimee: 100, actif: false },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockActions, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerEcoTips: vi.fn(),
  creerEcoTip: vi.fn(),
  modifierEcoTip: vi.fn(),
  supprimerEcoTip: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageEcoTips", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageEcoTips />);
    expect(screen.getByText(/Éco-Tips/)).toBeInTheDocument();
  });

  it("affiche les actions", () => {
    renderWithQuery(<PageEcoTips />);
    expect(screen.getByText("Compostage")).toBeInTheDocument();
    expect(screen.getByText("LED partout")).toBeInTheDocument();
  });

  it("affiche le nombre d'actions actives", () => {
    renderWithQuery(<PageEcoTips />);
    // 2 actives sur 3
    expect(screen.getByText(/2 action/)).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageEcoTips />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
