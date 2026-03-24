import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageContrats from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/contrats",
}));

const mockContrats = [
  { id: 1, nom: "Assurance habitation", type_contrat: "Assurance", fournisseur: "AXA", montant_mensuel: 45, date_debut: "2024-01-01", date_fin: "2027-01-01", statut: "actif" },
  { id: 2, nom: "Électricité EDF", type_contrat: "Énergie", fournisseur: "EDF", montant_mensuel: 80, date_debut: "2023-06-01", date_fin: "2026-06-01", statut: "actif" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key?.includes("alertes")) return { data: [], isLoading: false };
    if (key?.includes("resume")) return { data: { total_mensuel: 125, total_annuel: 1500 }, isLoading: false };
    return { data: mockContrats, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerContrats: vi.fn(),
  alertesContrats: vi.fn(),
  resumeFinancierContrats: vi.fn(),
  creerContrat: vi.fn(),
  modifierContrat: vi.fn(),
  supprimerContrat: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageContrats", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageContrats />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Contrats/);
  });

  it("affiche les contrats", () => {
    renderWithQuery(<PageContrats />);
    expect(screen.getByText("Assurance habitation")).toBeInTheDocument();
    expect(screen.getByText("Électricité EDF")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageContrats />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
