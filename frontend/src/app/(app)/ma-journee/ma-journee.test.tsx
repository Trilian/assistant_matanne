import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageMaJournee from "./page";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { nom: "Matanne" } }),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn().mockResolvedValue({ data: { items: [] } }),
  },
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (queryKey: unknown) => {
    const key = Array.isArray(queryKey) ? queryKey.join(":") : "";

    if (key.includes("tableau-bord")) {
      return { data: { repas_aujourd_hui: [] }, isLoading: false };
    }
    if (key.includes("taches-jour")) {
      return { data: [], isLoading: false, refetch: vi.fn() };
    }
    if (key.includes("activites")) {
      return { data: [], isLoading: false };
    }
    if (key.includes("routines")) {
      return { data: [], isLoading: false };
    }
    if (key.includes("anniversaires")) {
      return { data: [], isLoading: false };
    }

    return { data: undefined, isLoading: false, refetch: vi.fn() };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageMaJournee", () => {
  it("affiche les états vides principaux quand la journée est vide", () => {
    renderWithQuery(<PageMaJournee />);

    expect(screen.getByText(/Aucun repas planifié/i)).toBeInTheDocument();
    expect(screen.getByText(/Aucune activité prévue/i)).toBeInTheDocument();
  });
});
