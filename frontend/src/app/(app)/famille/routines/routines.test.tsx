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
  { id: 1, nom: "Routine matin", type: "matin", etapes: [{ titre: "Se lever" }, { titre: "Petit-déj" }] },
  { id: 2, nom: "Routine soir", type: "soir", etapes: [{ titre: "Bain" }, { titre: "Histoire" }] },
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
});
