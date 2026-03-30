import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Plan3D from "@/composants/maison/plan-3d";

vi.mock("@react-three/fiber", () => ({
  // Do not render children in JSDOM to avoid warnings from Three.js primitives.
  Canvas: () => <div data-testid="canvas" />,
}));

vi.mock("@react-three/drei", () => ({
  OrbitControls: () => <div data-testid="orbit-controls" />,
  Text: ({ children }: { children: React.ReactNode }) => <span>{children}</span>,
}));

describe("Plan3D", () => {
  it("affiche un message quand aucune pièce n'a de position", () => {
    render(
      <Plan3D pieces={[{ id: 1, nom: "Salon" } as never]} pieceSelectionnee={null} onSelectPiece={vi.fn()} />,
    );

    expect(screen.getByText(/Définissez les positions 2D/i)).toBeInTheDocument();
  });

  it("rend le canvas quand des pièces ont une position", () => {
    render(
      <Plan3D
        pieces={[
          {
            id: 1,
            nom: "Salon",
            position_x: 10,
            position_y: 10,
            largeur: 200,
            hauteur: 150,
          } as never,
        ]}
        pieceSelectionnee={null}
        onSelectPiece={vi.fn()}
      />,
    );

    expect(screen.getByTestId("canvas")).toBeInTheDocument();
  });
});
