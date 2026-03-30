import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { FormulaireRecette } from "@/composants/cuisine/formulaire-recette";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("FormulaireRecette", () => {
  beforeEach(() => {
    push.mockReset();
  });

  it("affiche le mode création", () => {
    render(<FormulaireRecette />);

    expect(screen.getByText("➕ Nouvelle recette")).toBeInTheDocument();
    expect(screen.getAllByText("Générer depuis une photo").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Choisir une photo pour générer une recette")).toBeInTheDocument();
  });

  it("affiche le mode édition", () => {
    render(
      <FormulaireRecette
        recetteExistante={{
          id: 42,
          nom: "Tarte tomate",
          description: "Délicieuse",
          instructions: "Cuire 30 min",
          ingredients: [{ nom: "Tomate", quantite: 2, unite: "pièce" }],
        } as never}
      />,
    );

    expect(screen.getByText("✏️ Modifier la recette")).toBeInTheDocument();
    expect(screen.queryByText("Générer depuis une photo")).not.toBeInTheDocument();
  });
});
