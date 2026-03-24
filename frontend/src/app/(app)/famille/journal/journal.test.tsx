import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageJournal from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/journal",
}));

const mockEntrees = [
  { id: 1, contenu: "Première dent de Jules sortie", humeur: "bien", gratitudes: [], tags: ["jules"], date_entree: "2026-03-20", cree_le: "2026-03-20" },
  { id: 2, contenu: "Journée jeux de société en famille", humeur: "neutre", gratitudes: [], tags: ["weekend"], date_entree: "2026-03-15", cree_le: "2026-03-15" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockEntrees, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/utilitaires", () => ({
  listerJournal: vi.fn(),
  creerEntreeJournal: vi.fn(),
  supprimerEntreeJournal: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageJournal", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageJournal />);
    expect(screen.getByText(/Journal/)).toBeInTheDocument();
  });

  it("affiche les entrées", () => {
    renderWithQuery(<PageJournal />);
    expect(screen.getByText(/Première dent de Jules sortie/)).toBeInTheDocument();
    expect(screen.getByText(/Journée jeux de société en famille/)).toBeInTheDocument();
  });

  it("affiche le bouton nouvelle entrée", () => {
    renderWithQuery(<PageJournal />);
    expect(screen.getByText(/Nouvelle entrée/)).toBeInTheDocument();
  });
});
