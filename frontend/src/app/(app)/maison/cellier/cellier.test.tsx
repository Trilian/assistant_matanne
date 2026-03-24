import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageCellier from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/cellier",
}));

const mockArticles = [
  { id: 1, nom: "Bordeaux 2019", categorie: "Vin", quantite: 6, unite: "bouteilles", emplacement: "Cave", date_peremption: "2030-01-01", prix_unitaire: 12 },
  { id: 2, nom: "Confiture fraise", categorie: "Conserve", quantite: 3, unite: "pots", emplacement: "Cellier", date_peremption: "2026-06-15", prix_unitaire: 4 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key.includes("alertes-peremption")) return { data: [mockArticles[1]], isLoading: false };
    if (key.includes("stats")) return { data: { total_articles: 2, valeur_totale: 84 }, isLoading: false };
    return { data: mockArticles, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerArticlesCellier: vi.fn(),
  creerArticleCellier: vi.fn(),
  modifierArticleCellier: vi.fn(),
  supprimerArticleCellier: vi.fn(),
  alertesPeremptionCellier: vi.fn(),
  statsCellier: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageCellier", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageCellier />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Cellier/);
  });

  it("affiche les articles", () => {
    renderWithQuery(<PageCellier />);
    expect(screen.getAllByText(/Bordeaux 2019/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/Confiture fraise/).length).toBeGreaterThanOrEqual(1);
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageCellier />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
