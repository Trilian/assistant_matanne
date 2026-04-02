import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageBatchCooking from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/batch-cooking",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockSessions = [
  { id: 1, nom: "Batch dimanche", statut: "planifie", date_session: "2025-01-26", duree_estimee: 180, recettes_selectionnees: [] },
  { id: 2, nom: "Prep semaine", statut: "termine", date_session: "2025-01-19", duree_estimee: 120, recettes_selectionnees: [] },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: { items: mockSessions }, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/batch-cooking", () => ({
  listerSessionsBatch: vi.fn(),
  creerSessionBatch: vi.fn(),
  supprimerSessionBatch: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageBatchCooking", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Batch Cooking", () => {
    renderWithQuery(<PageBatchCooking />);
    expect(screen.getByText(/Batch Cooking/)).toBeInTheDocument();
  });

  it("affiche les sessions", () => {
    renderWithQuery(<PageBatchCooking />);
    expect(screen.getAllByText("Batch dimanche").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Prep semaine").length).toBeGreaterThan(0);
  });
});
