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
        return { id: "1" };
      }
      return value;
    },
  };
});

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/recettes/1/modifier",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: { id: 1, nom: "Poulet rôti", ingredients: [], etapes: [] },
    isLoading: false,
  }),
}));

vi.mock("@/bibliotheque/api/recettes", () => ({
  obtenirRecette: vi.fn(),
}));

vi.mock("@/composants/cuisine/formulaire-recette", () => ({
  FormulaireRecette: ({ recetteExistante }: { recetteExistante?: { nom: string } }) => (
    <div data-testid="formulaire-recette">{recetteExistante?.nom ?? "Nouveau"}</div>
  ),
}));

const PageModifierRecette = (await import("./page")).default;

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageModifierRecette", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le formulaire avec la recette", () => {
    renderWithQuery(<PageModifierRecette params={Promise.resolve({ id: "1" })} />);
    expect(screen.getByTestId("formulaire-recette")).toBeInTheDocument();
    expect(screen.getByText("Poulet rôti")).toBeInTheDocument();
  });
});
