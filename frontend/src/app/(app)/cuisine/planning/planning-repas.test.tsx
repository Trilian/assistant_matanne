import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PagePlanningRepas from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/planning",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: { repas: [] }, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/planning", () => ({
  obtenirPlanningSemaine: vi.fn(),
  definirRepas: vi.fn(),
  supprimerRepas: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PagePlanningRepas", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Planning Repas", () => {
    renderWithQuery(<PagePlanningRepas />);
    expect(screen.getByText(/Planning/i)).toBeInTheDocument();
  });

  it("affiche les jours de la semaine", () => {
    renderWithQuery(<PagePlanningRepas />);
    expect(screen.getByText("Lundi")).toBeInTheDocument();
    expect(screen.getByText("Dimanche")).toBeInTheDocument();
  });
});
