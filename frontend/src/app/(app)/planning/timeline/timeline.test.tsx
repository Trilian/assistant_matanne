import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageTimeline from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/planning/timeline",
}));

vi.mock("next/link", () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockPlanning = {
  repas: [
    { id: 1, date: "2026-03-23", type_repas: "dejeuner" as const, recette_nom: "Pâtes carbonara", notes: null, portions: 4 },
    { id: 2, date: "2026-03-23", type_repas: "diner" as const, recette_nom: "Salade niçoise", notes: null, portions: 4 },
    { id: 3, date: "2026-03-24", type_repas: "dejeuner" as const, recette_nom: "Poulet rôti", notes: null, portions: 4 },
  ],
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockPlanning, isLoading: false }),
}));

vi.mock("@/bibliotheque/api/planning", () => ({
  obtenirPlanningSemaine: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageTimeline", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageTimeline />);
    expect(screen.getByText(/Timeline/)).toBeInTheDocument();
  });

  it("affiche les repas groupés par date", () => {
    renderWithQuery(<PageTimeline />);
    expect(screen.getByText("Pâtes carbonara")).toBeInTheDocument();
    expect(screen.getByText("Salade niçoise")).toBeInTheDocument();
    expect(screen.getByText("Poulet rôti")).toBeInTheDocument();
  });

  it("affiche le lien retour Calendrier", () => {
    renderWithQuery(<PageTimeline />);
    expect(screen.getByText("Calendrier")).toBeInTheDocument();
  });
});
