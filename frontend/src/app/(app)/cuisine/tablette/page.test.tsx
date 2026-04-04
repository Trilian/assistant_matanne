import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

import PageTabletteCuisine from "./page";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key[0] === "planning") {
      return {
        data: {
          repas: [
            {
              id: 1,
              recette_id: 99,
              recette_nom: "Gratin de légumes",
              type_repas: "diner",
              date_repas: "2099-01-01",
              portions: 4,
              plat_jules: "Purée de légumes sans sel",
            },
          ],
        },
        isLoading: false,
        refetch: vi.fn(),
      };
    }

    if (key[0] === "recettes") {
      return {
        data: {
          id: 99,
          nom: "Gratin de légumes",
          temps_preparation: 15,
          temps_cuisson: 25,
          portions: 4,
          ingredients: [
            { nom: "Courgettes", quantite: 2, unite: "pcs" },
            { nom: "Crème", quantite: 20, unite: "cl" },
          ],
          instructions: "Préchauffer le four\nCouper les légumes\nEnfourner 25 minutes",
        },
        isLoading: false,
      };
    }

    if (key[0] === "courses" && key[2] === "listes") {
      return {
        data: [{ id: 7, nom: "Courses semaine", etat: "en_cours" }],
        isLoading: false,
      };
    }

    if (key[0] === "courses") {
      return {
        data: {
          id: 7,
          nom: "Courses semaine",
          articles: [
            { id: 1, nom: "Lait", est_coche: false, quantite: 1, unite: "L", categorie: "Frais" },
          ],
        },
        isLoading: false,
      };
    }

    return { data: null, isLoading: false };
  }),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageTabletteCuisine", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    Object.defineProperty(window, "speechSynthesis", {
      configurable: true,
      value: {
        speak: vi.fn(),
        cancel: vi.fn(),
      },
    });

    class MockSpeechSynthesisUtterance {
      text: string;
      lang = "fr-FR";
      rate = 1;
      pitch = 1;
      volume = 1;
      onstart: (() => void) | null = null;
      onend: (() => void) | null = null;
      onerror: (() => void) | null = null;

      constructor(text: string) {
        this.text = text;
      }
    }

    Object.defineProperty(window, "SpeechSynthesisUtterance", {
      configurable: true,
      value: MockSpeechSynthesisUtterance,
    });

    Object.defineProperty(HTMLElement.prototype, "requestFullscreen", {
      configurable: true,
      value: vi.fn().mockResolvedValue(undefined),
    });

    Object.defineProperty(document, "exitFullscreen", {
      configurable: true,
      value: vi.fn().mockResolvedValue(undefined),
    });
  });

  it("affiche le mode guidé et permet la lecture vocale de l'étape courante", async () => {
    const user = userEvent.setup();
    renderWithQuery(<PageTabletteCuisine />);

    expect(screen.getByText(/mode guidé pas à pas/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /lire l'étape/i }));

    expect(window.speechSynthesis.cancel).toHaveBeenCalled();
    expect(window.speechSynthesis.speak).toHaveBeenCalledTimes(1);
  });

  it("propose le basculement en plein écran natif", async () => {
    const user = userEvent.setup();
    renderWithQuery(<PageTabletteCuisine />);

    await user.click(screen.getByRole("button", { name: /plein écran natif/i }));

    expect(HTMLElement.prototype.requestFullscreen).toHaveBeenCalled();
  });
});
