import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageDiagnostics from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/diagnostics",
}));

const mockDiagnostics = [
  { id: 1, type_diagnostic: "DPE", date_realisation: "2024-01-15", date_expiration: "2034-01-15", resultat: "C", diagnostiqueur: "DiagExpert" },
  { id: 2, type_diagnostic: "Amiante", date_realisation: "2023-06-01", date_expiration: "2026-06-01", resultat: "Négatif", diagnostiqueur: "LabAnalyse" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key?.includes("alertes")) return { data: [], isLoading: false };
    if (key?.includes("estimations")) return { data: [], isLoading: false };
    if (key?.includes("derniere")) return { data: null, isLoading: false };
    return { data: mockDiagnostics, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerDiagnostics: vi.fn(),
  alertesDiagnostics: vi.fn(),
  listerEstimations: vi.fn(),
  derniereEstimation: vi.fn(),
  creerDiagnostic: vi.fn(),
  modifierDiagnostic: vi.fn(),
  supprimerDiagnostic: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageDiagnostics", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageDiagnostics />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Diagnostics/);
  });

  it("affiche les diagnostics", () => {
    renderWithQuery(<PageDiagnostics />);
    expect(screen.getByText("DPE")).toBeInTheDocument();
    expect(screen.getByText("Amiante")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageDiagnostics />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
