import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PagePlanning from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/planning",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: { repas: [] }, isLoading: false, error: null }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/planning", () => ({
  obtenirPlanningSemaine: vi.fn(),
  definirRepas: vi.fn(),
  supprimerRepas: vi.fn(),
  genererPlanningSemaine: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PagePlanning", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Planning", () => {
    renderWithQuery(<PagePlanning />);
    expect(screen.getByRole("heading", { name: /Planning/ })).toBeInTheDocument();
  });

  it("affiche les jours de la semaine", () => {
    renderWithQuery(<PagePlanning />);
    expect(screen.getByText("Lundi")).toBeInTheDocument();
    expect(screen.getByText("Dimanche")).toBeInTheDocument();
  });
});
