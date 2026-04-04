import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageDocuments from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/documents",
}));

const mockDocuments = {
  items: [
    { id: 1, titre: "Carnet de santé Jules", categorie: "sante", membre_famille: "Jules", date_document: "2026-01-15", date_expiration: null, notes: "", est_expire: false },
    { id: 2, titre: "Bail appartement", categorie: "administratif", membre_famille: null, date_document: "2025-09-01", date_expiration: "2027-09-01", notes: "", est_expire: false },
  ],
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockDocuments, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/documents", () => ({
  listerDocuments: vi.fn(),
  creerDocument: vi.fn(),
  modifierDocument: vi.fn(),
  supprimerDocument: vi.fn(),
  extraireDocumentOCR: vi.fn(),
}));

vi.mock("@/bibliotheque/api/ia-avancee", () => ({
  analyserDocument: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageDocuments", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageDocuments />);
    expect(screen.getByText(/Documents/)).toBeInTheDocument();
  });

  it("affiche les documents", () => {
    renderWithQuery(<PageDocuments />);
    expect(screen.getByText("Carnet de santé Jules")).toBeInTheDocument();
    expect(screen.getByText("Bail appartement")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageDocuments />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
    expect(screen.getByText(/préremplit le formulaire/i)).toBeInTheDocument();
  });
});
