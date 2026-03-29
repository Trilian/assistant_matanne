// ═══════════════════════════════════════════════════════════
// Tests — Page Outils/Nutritionniste
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// Mock de toutes les dépendances API
vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));
vi.mock("@/bibliotheque/api/outils", () => ({
  envoyerMessageChat: vi.fn(),
  obtenirActionsRapides: vi.fn(),
}));
vi.mock("@/bibliotheque/api/planning", () => ({
  obtenirNutritionHebdo: vi.fn(),
}));
vi.mock("@/composants/ui/bouton-vocal", () => ({
  BoutonVocal: () => React.createElement("div", { "data-testid": "bouton-vocal" }),
}));

import { envoyerMessageChat } from "@/bibliotheque/api/outils";
import { obtenirNutritionHebdo } from "@/bibliotheque/api/planning";
import NutritionistePage from "@/app/(app)/outils/nutritionniste/page";

const mockedChat = vi.mocked(envoyerMessageChat);
const mockedNutrition = vi.mocked(obtenirNutritionHebdo);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

beforeEach(() => {
  vi.clearAllMocks();
  mockedNutrition.mockResolvedValue({
    calories_total: 1800,
    proteines_g: 80,
    lipides_g: 60,
    glucides_g: 220,
    nb_repas: 21,
  } as never);
});

describe("NutritionistePage — rendu initial", () => {
  it("affiche le titre du module nutritionniste", () => {
    renderWithQuery(React.createElement(NutritionistePage));
    // Le titre contient "nutrition" ou "nutritionniste"
    const heading = screen.getAllByText(/nutri/i);
    expect(heading.length).toBeGreaterThan(0);
  });

  it("affiche les actions rapides de nutrition", () => {
    renderWithQuery(React.createElement(NutritionistePage));
    expect(screen.getByText(/Analyser mon repas/i)).toBeDefined();
  });

  it("affiche le bilan nutritionnel hebdomadaire après chargement", async () => {
    renderWithQuery(React.createElement(NutritionistePage));
    await waitFor(() => {
      // Les calories de la semaine doivent apparaître
      expect(screen.getByText(/1\s*800|1800/)).toBeDefined();
    });
  });
});

describe("NutritionistePage — envoi message", () => {
  it("appelle envoyerMessageChat lors de l'envoi", async () => {
    mockedChat.mockResolvedValue({
      reponse: "Votre repas est bien équilibré.",
      tokens_utilises: 150,
    } as never);

    renderWithQuery(React.createElement(NutritionistePage));

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Analyse mon repas" } });

    const sendBtn = screen.getByRole("button", { name: /envoyer/i });
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(mockedChat).toHaveBeenCalled();
    });
  });

  it("affiche la réponse IA dans le fil de messages", async () => {
    mockedChat.mockResolvedValue({
      reponse: "Votre repas est bien équilibré.",
      tokens_utilises: 150,
    } as never);

    renderWithQuery(React.createElement(NutritionistePage));

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Analyse mon repas" } });
    fireEvent.submit(input.closest("form") ?? input);

    await waitFor(() => {
      expect(screen.getByText(/équilibré/i)).toBeDefined();
    });
  });
});
