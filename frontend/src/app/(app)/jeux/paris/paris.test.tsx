import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ParisPage from "@/app/(app)/jeux/paris/page";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  };
}

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/jeux/paris",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockStats = {
  total_paris: 25,
  total_mise: 500,
  benefice: 125,
  taux_reussite: 0.56,
};

const mockParis = [
  {
    id: 1,
    match_id: 10,
    type_pari: "1X2",
    prediction: "PSG",
    cote: 1.85,
    mise: 20,
    gain: 37,
    statut: "gagne",
  },
  {
    id: 2,
    match_id: 11,
    type_pari: "1X2",
    prediction: "Monaco",
    cote: 2.1,
    mise: 15,
    gain: 0,
    statut: "perdu",
  },
];

const mockMatchs = [
  { id: 10, equipe_domicile: "PSG", equipe_exterieur: "OM" },
  { id: 11, equipe_domicile: "Lyon", equipe_exterieur: "Monaco" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("stats")) {
      return { data: mockStats, isLoading: false, error: null };
    }
    if (key.includes("matchs")) {
      return { data: mockMatchs, isLoading: false, error: null };
    }
    return { data: mockParis, isLoading: false, error: null };
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("ParisPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre Paris Sportifs", () => {
    render(<ParisPage />, { wrapper: createWrapper() });
    expect(screen.getByText(/Paris Sportifs/)).toBeInTheDocument();
  });

  it("affiche les 4 cartes statistiques", () => {
    render(<ParisPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Total paris")).toBeInTheDocument();
    expect(screen.getByText("Mises totales")).toBeInTheDocument();
    expect(screen.getByText("Bénéfice")).toBeInTheDocument();
    expect(screen.getByText("Taux réussite")).toBeInTheDocument();
  });

  it("affiche les boutons de filtre", () => {
    render(<ParisPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Tous")).toBeInTheDocument();
  });

  it("affiche l'historique des paris avec noms de matchs", () => {
    render(<ParisPage />, { wrapper: createWrapper() });
    expect(screen.getByText("PSG vs OM")).toBeInTheDocument();
    expect(screen.getByText("Lyon vs Monaco")).toBeInTheDocument();
  });

  it("affiche le tableau Historique des paris", () => {
    render(<ParisPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Historique des paris")).toBeInTheDocument();
  });
});
