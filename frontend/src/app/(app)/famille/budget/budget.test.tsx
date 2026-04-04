import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import BudgetPage from "@/app/(app)/famille/budget/page";

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
  usePathname: () => "/famille/budget",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/composants/famille/budget-insights", () => ({
  BudgetInsightsIA: () => <div data-testid="budget-insights-ia">Insights IA</div>,
}));

const mockStats = {
  total_mois: 1250,
  categories: [
    { nom: "alimentation", montant: 450, pourcentage: 36 },
    { nom: "logement", montant: 500, pourcentage: 40 },
    { nom: "transport", montant: 150, pourcentage: 12 },
    { nom: "loisirs", montant: 150, pourcentage: 12 },
  ],
};

const mockDepenses = [
  {
    id: 1,
    libelle: "Courses Carrefour",
    montant: 85.5,
    categorie: "alimentation",
    date: "2024-12-01",
  },
  {
    id: 2,
    libelle: "Essence",
    montant: 65.0,
    categorie: "transport",
    date: "2024-12-02",
  },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("stats")) {
      return { data: mockStats, isLoading: false, error: null };
    }
    return { data: mockDepenses, isLoading: false, error: null };
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("BudgetPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre Budget", () => {
    render(<BudgetPage />, { wrapper: createWrapper() });
    expect(screen.getByText(/Budget/)).toBeInTheDocument();
  });

  it("affiche la carte Total du mois", () => {
    render(<BudgetPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Total du mois")).toBeInTheDocument();
  });

  it("affiche la section Répartition par catégorie", () => {
    render(<BudgetPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Répartition par catégorie")).toBeInTheDocument();
  });

  it("affiche les dépenses listées", () => {
    render(<BudgetPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Courses Carrefour")).toBeInTheDocument();
    expect(screen.getByText("Essence")).toBeInTheDocument();
  });

  it("affiche le filtre catégorie", () => {
    render(<BudgetPage />, { wrapper: createWrapper() });
    expect(screen.getByText(/Dépenses/)).toBeInTheDocument();
  });
});
