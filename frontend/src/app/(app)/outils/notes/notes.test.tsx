import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import NotesPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/outils/notes",
}));

const mockNotes = [
  { id: 1, titre: "Courses samedi", contenu: "Pain, lait, oeufs", categorie: "course", epingle: true, archive: false, couleur: "#fef08a", tags: ["course"] },
  { id: 2, titre: "Idée weekend", contenu: "Zoo de Vincennes", categorie: "idee", epingle: false, archive: false, couleur: "#bbf7d0", tags: [] },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockNotes, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/outils", () => ({
  listerNotes: vi.fn(),
  creerNote: vi.fn(),
  modifierNote: vi.fn(),
  supprimerNote: vi.fn(),
}));

vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("NotesPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<NotesPage />);
    expect(screen.getByText(/Notes/)).toBeInTheDocument();
  });

  it("affiche les notes", () => {
    renderWithQuery(<NotesPage />);
    expect(screen.getByText(/Courses samedi/)).toBeInTheDocument();
    expect(screen.getByText(/Idée weekend/)).toBeInTheDocument();
  });

  it("affiche le bouton nouvelle note", () => {
    renderWithQuery(<NotesPage />);
    expect(screen.getByText(/Nouvelle note/)).toBeInTheDocument();
  });

  it("affiche le champ de recherche", () => {
    renderWithQuery(<NotesPage />);
    expect(screen.getByPlaceholderText(/Rechercher/)).toBeInTheDocument();
  });
});
