import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import PageNouvelleRecette from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/recettes/nouveau",
}));

vi.mock("@/composants/cuisine/formulaire-recette", () => ({
  FormulaireRecette: () => <div data-testid="formulaire-recette">Formulaire Recette</div>,
}));

describe("PageNouvelleRecette", () => {
  it("affiche le formulaire de création", () => {
    render(<PageNouvelleRecette />);
    expect(screen.getByTestId("formulaire-recette")).toBeInTheDocument();
  });
});
