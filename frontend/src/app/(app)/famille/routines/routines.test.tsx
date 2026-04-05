import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageRoutines from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/routines",
}));

const mockRoutines = [
  {
    id: 1,
    nom: "Routine matin",
    type: "matin",
    etapes: [
      { id: 11, titre: "Se lever", ordre: 1, est_terminee: false },
      { id: 12, titre: "Petit-déj", ordre: 2, est_terminee: false },
    ],
  },
  {
    id: 2,
    nom: "Routine soir",
    type: "soir",
    etapes: [
      { id: 21, titre: "Bain", ordre: 1, est_terminee: false },
      { id: 22, titre: "Histoire", ordre: 2, est_terminee: false },
    ],
  },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockRoutines, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerRoutines: vi.fn(),
  creerRoutine: vi.fn(),
  supprimerRoutine: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageRoutines", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Routines", () => {
    renderWithQuery(<PageRoutines />);
    expect(screen.getByRole("heading", { name: /Routines/ })).toBeInTheDocument();
  });

  it("affiche les routines existantes", () => {
    renderWithQuery(<PageRoutines />);
    expect(screen.getByText("Routine matin")).toBeInTheDocument();
    expect(screen.getByText("Routine soir")).toBeInTheDocument();
  });

  it("affiche une heatmap de régularité pour les routines", () => {
    renderWithQuery(<PageRoutines />);
    expect(screen.getByText("Régularité des routines")).toBeInTheDocument();
    expect(screen.getByText(/12 dernières semaines/i)).toBeInTheDocument();
  });
});
