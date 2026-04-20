import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GenerateurGrille } from "./generateur-grille";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
const wrap = (ui: React.ReactNode) => (
  <QueryClientProvider client={qc}>{ui}</QueryClientProvider>
);

describe("GenerateurGrille", () => {
  const mockFn = vi.fn().mockResolvedValue({
    numeros: [1, 2, 3, 4, 5],
    special: [7],
    strategie: "statistique",
  });

  it("affiche les 3 stratégies", () => {
    render(
      wrap(
        <GenerateurGrille typeJeu="loto" genererFn={mockFn} />
      )
    );
    expect(screen.getByText(/Statistique/)).toBeDefined();
    expect(screen.getByText(/Aléatoire/)).toBeDefined();
    expect(screen.getByText(/IA/)).toBeDefined();
  });

  it("affiche le bouton générer", () => {
    render(
      wrap(
        <GenerateurGrille typeJeu="loto" genererFn={mockFn} />
      )
    );
    expect(screen.getByText(/Générer une grille/)).toBeDefined();
  });

  it("appelle genererFn au clic", async () => {
    const user = userEvent.setup();
    render(
      wrap(
        <GenerateurGrille typeJeu="euromillions" genererFn={mockFn} />
      )
    );
    await user.click(screen.getByText(/Générer une grille/));
    expect(mockFn).toHaveBeenCalledWith("statistique", false);
  });

  it("permet de changer de stratégie", async () => {
    const user = userEvent.setup();
    render(
      wrap(
        <GenerateurGrille typeJeu="loto" genererFn={mockFn} />
      )
    );
    await user.click(screen.getByText(/Aléatoire/));
    await user.click(screen.getByText(/Générer une grille/));
    expect(mockFn).toHaveBeenCalledWith("aleatoire", false);
  });
});
