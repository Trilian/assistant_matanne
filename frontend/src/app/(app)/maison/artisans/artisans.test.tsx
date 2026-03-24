import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageArtisans from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/artisans",
}));

const mockArtisans = [
  { id: 1, nom: "Dupont Plomberie", metier: "Plombier", telephone: "0612345678", email: "dupont@test.fr", adresse: "Paris", note_satisfaction: 4.5 },
  { id: 2, nom: "Martin Électricité", metier: "Électricien", telephone: "0698765432", email: "martin@test.fr", adresse: "Lyon", note_satisfaction: 5 },
];

const mockStats = { total_artisans: 2, total_interventions: 5, depenses_totales: 1200, par_metier: { Plombier: 1, "Électricien": 1 } };

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key?.includes("stats")) return { data: mockStats, isLoading: false };
    return { data: mockArtisans, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerArtisans: vi.fn(),
  creerArtisan: vi.fn(),
  modifierArtisan: vi.fn(),
  supprimerArtisan: vi.fn(),
  statsArtisans: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageArtisans", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageArtisans />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Artisans/);
  });

  it("affiche les artisans", () => {
    renderWithQuery(<PageArtisans />);
    expect(screen.getByText("Dupont Plomberie")).toBeInTheDocument();
    expect(screen.getByText("Martin Électricité")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageArtisans />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });
});
