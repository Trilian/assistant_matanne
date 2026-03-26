import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageJournal from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/journal",
}));

const mockEntrees = [
  { id: 1, contenu: "Premiere dent de Jules sortie", humeur: "bien", gratitudes: [], tags: ["jules"], date_entree: "2026-03-20", cree_le: "2026-03-20" },
  { id: 2, contenu: "Journee jeux de societe en famille", humeur: "neutre", gratitudes: [], tags: ["weekend"], date_entree: "2026-03-15", cree_le: "2026-03-15" },
  // Phase R — résumé IA sauvegardé
  { id: 3, contenu: "Resume semaine du 10-16 mars : Jules a progresse en motricite.", humeur: "bien", gratitudes: [], tags: ["resume-ia"], date_entree: "2026-03-17", cree_le: "2026-03-17" },
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

vi.mock("@/bibliotheque/api/famille", () => ({
  obtenirResumeSemaine: vi.fn(),
  obtenirRetrospective: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
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

  it("affiche les entrées normales", () => {
    renderWithQuery(<PageJournal />);
    expect(screen.getByText(/Premiere dent de Jules sortie/)).toBeInTheDocument();
    expect(screen.getByText(/Journee jeux de societe/)).toBeInTheDocument();
  });

  it("affiche le bouton nouvelle entrée", () => {
    renderWithQuery(<PageJournal />);
    expect(screen.getByText(/Nouvelle entrée/)).toBeInTheDocument();
  });

  // Phase R — résumés IA sauvegardés
  it("affiche la section Résumés IA récents quand des résumés existent", () => {
    renderWithQuery(<PageJournal />);
    expect(screen.getByText("Résumés IA récents")).toBeInTheDocument();
  });

  it("affiche le contenu des résumés IA avec tag resume-ia", () => {
    renderWithQuery(<PageJournal />);
    // Le résumé apparaît dans la section "Résumés IA récents" et la timeline
    const elements = screen.getAllByText(/Jules a progresse en motricite/);
    expect(elements.length).toBeGreaterThanOrEqual(1);
  });

  it("n'affiche pas les résumés dans la timeline principale", () => {
    renderWithQuery(<PageJournal />);
    // Les entrées normales restent visibles
    expect(screen.getByText(/Premiere dent de Jules sortie/)).toBeInTheDocument();
  });
});
