import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FormulaireRecette } from "@/composants/cuisine/formulaire-recette";

const push = vi.fn();
const mutationMutate = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserMutation: vi.fn(() => ({ mutate: mutationMutate, isPending: false })),
  utiliserInvalidation: () => vi.fn(),
}));

describe("FormulaireRecette", () => {
  beforeEach(() => {
    push.mockReset();
    mutationMutate.mockReset();
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

  it("permet d'ajouter puis retirer un ingrédient", async () => {
    const user = userEvent.setup();
    render(<FormulaireRecette />);

    expect(screen.getAllByPlaceholderText("Ingrédient")).toHaveLength(1);

    await user.click(screen.getByRole("button", { name: /^Ajouter$/i }));
    expect(screen.getAllByPlaceholderText("Ingrédient")).toHaveLength(2);

    await user.click(screen.getAllByRole("button", { name: /Retirer l'ingrédient/i })[0]);
    expect(screen.getAllByPlaceholderText("Ingrédient")).toHaveLength(1);
  });

  it("affiche une erreur de validation si le nom est trop court", async () => {
    const user = userEvent.setup();
    render(<FormulaireRecette />);

    await user.type(screen.getByLabelText("Nom *"), "A");

    const ingredientInput = screen.getByPlaceholderText("Ingrédient");
    await user.type(ingredientInput, "Pommes de terre");

    await user.click(screen.getByRole("button", { name: /Créer la recette/i }));

    expect(await screen.findByText("Nom requis")).toBeInTheDocument();
    expect(mutationMutate).not.toHaveBeenCalled();
  });
});
