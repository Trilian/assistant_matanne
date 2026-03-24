import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageAnniversaires from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/anniversaires",
}));

const mockAnniversaires = [
  { id: 1, nom_personne: "Jules", date_naissance: "2024-05-15", relation: "enfant", rappel_jours_avant: 7, idees_cadeaux: "Lego, Livres", notes: "" },
  { id: 2, nom_personne: "Mamie Dupont", date_naissance: "1955-12-01", relation: "grand_parent", rappel_jours_avant: 14, idees_cadeaux: "Fleurs", notes: "" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockAnniversaires, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerAnniversaires: vi.fn(),
  creerAnniversaire: vi.fn(),
  modifierAnniversaire: vi.fn(),
  supprimerAnniversaire: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageAnniversaires", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageAnniversaires />);
    expect(screen.getByText(/Anniversaires/)).toBeInTheDocument();
  });

  it("affiche les anniversaires", () => {
    renderWithQuery(<PageAnniversaires />);
    expect(screen.getAllByText(/Jules/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Mamie Dupont")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageAnniversaires />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
