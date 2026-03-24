import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageActivites from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/activites",
}));

const mockActivites = [
  { id: 1, titre: "Parc", type: "sortie", date: "2025-01-25", lieu: "Lyon", duree: 120 },
  { id: 2, titre: "Piscine", type: "sport", date: "2025-01-26", lieu: "Paris", duree: 60 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockActivites, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerActivites: vi.fn(),
  creerActivite: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageActivites", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Activités", () => {
    renderWithQuery(<PageActivites />);
    expect(screen.getByRole("heading", { name: /Activit/ })).toBeInTheDocument();
  });

  it("affiche les activités", () => {
    renderWithQuery(<PageActivites />);
    expect(screen.getByText("Parc")).toBeInTheDocument();
    expect(screen.getByText("Piscine")).toBeInTheDocument();
  });
});
