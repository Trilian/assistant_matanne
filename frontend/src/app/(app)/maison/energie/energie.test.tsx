import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageEnergie from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/energie",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: [], isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerReleves: vi.fn(),
  creerReleve: vi.fn(),
  supprimerReleve: vi.fn(),
  historiqueEnergie: vi.fn(),
}));

vi.mock("@/composants/dialogue-formulaire", () => ({
  DialogueFormulaire: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageEnergie", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Énergie", () => {
    renderWithQuery(<PageEnergie />);
    expect(screen.getByText(/nergie/)).toBeInTheDocument();
  });

  it("affiche les onglets de compteurs", () => {
    renderWithQuery(<PageEnergie />);
    expect(screen.getByText("Électricité")).toBeInTheDocument();
    expect(screen.getByText("Eau")).toBeInTheDocument();
    expect(screen.getByText("Gaz")).toBeInTheDocument();
  });
});
