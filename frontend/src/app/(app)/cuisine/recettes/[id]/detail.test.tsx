import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// Mock React.use() to synchronously unwrap params Promise
vi.mock("react", async () => {
  const actual = await vi.importActual("react");
  return {
    ...actual,
    use: (value: unknown) => {
      if (value instanceof Promise) {
        // For resolved params, return the value directly
        return { id: "1" };
      }
      return value;
    },
  };
});

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/recettes/1",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockRecette = {
  id: 1,
  nom: "Poulet rôti",
  temps_preparation: 15,
  temps_cuisson: 60,
  portions: 4,
  difficulte: "facile",
  ingredients: [{ nom: "Poulet", quantite: "1", unite: "pièce" }],
  etapes: ["Préchauffer le four", "Enfourner"],
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockRecette, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/recettes", () => ({
  obtenirRecette: vi.fn(),
  supprimerRecette: vi.fn(),
}));

// Dynamically import so `use(params)` is handled after mocks
const PageRecetteDetail = (await import("./page")).default;

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageRecetteDetail", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le nom de la recette", () => {
    renderWithQuery(<PageRecetteDetail params={Promise.resolve({ id: "1" })} />);
    expect(screen.getByText("Poulet rôti")).toBeInTheDocument();
  });

  it("affiche les informations de temps", () => {
    renderWithQuery(<PageRecetteDetail params={Promise.resolve({ id: "1" })} />);
    expect(screen.getByText(/15/)).toBeInTheDocument();
    expect(screen.getByText(/60/)).toBeInTheDocument();
  });
});
