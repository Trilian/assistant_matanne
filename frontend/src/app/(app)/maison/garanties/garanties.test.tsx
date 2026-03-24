import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageGaranties from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/garanties",
}));

const mockGaranties = [
  { id: 1, appareil: "Lave-linge", marque: "Samsung", date_achat: "2024-03-15", date_fin_garantie: "2027-03-15", piece: "Buanderie", magasin: "Darty", prix_achat: 599 },
  { id: 2, appareil: "Four", marque: "Bosch", date_achat: "2023-11-01", date_fin_garantie: "2026-11-01", piece: "Cuisine", magasin: "Boulanger", prix_achat: 450 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key.includes("alertes")) return { data: [], isLoading: false };
    if (key.includes("stats")) return { data: { total: 2, valeur_totale: 1049 }, isLoading: false };
    return { data: mockGaranties, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerGaranties: vi.fn(),
  alertesGaranties: vi.fn(),
  statsGaranties: vi.fn(),
  creerGarantie: vi.fn(),
  modifierGarantie: vi.fn(),
  supprimerGarantie: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageGaranties", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageGaranties />);
    expect(screen.getByText(/Garanties/)).toBeInTheDocument();
  });

  it("affiche les garanties", () => {
    renderWithQuery(<PageGaranties />);
    expect(screen.getByText("Lave-linge")).toBeInTheDocument();
    expect(screen.getByText("Four")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageGaranties />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
