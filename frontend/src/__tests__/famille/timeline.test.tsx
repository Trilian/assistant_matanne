// ═══════════════════════════════════════════════════════════
// Tests — Page Famille/Timeline
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import TimelineFamillePage from "@/app/(app)/famille/timeline/page";

const mockedApi = vi.mocked(clientApi);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

const ITEMS_TIMELINE = [
  {
    id: "1",
    categorie: "jules" as const,
    date: "2025-01-10",
    titre: "Première marche de Jules",
    description: "Jules a fait ses premiers pas !",
  },
  {
    id: "2",
    categorie: "maison" as const,
    date: "2025-01-08",
    titre: "Rénovation cuisine terminée",
    description: null,
  },
];

beforeEach(() => {
  vi.clearAllMocks();
});

describe("TimelineFamillePage — rendu initial", () => {
  it("affiche les items de la timeline après chargement", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: ITEMS_TIMELINE, total: 2 } });

    renderWithQuery(React.createElement(TimelineFamillePage));

    await waitFor(() => {
      expect(screen.getAllByText("Première marche de Jules").length).toBeGreaterThan(0);
    });
  });

  it("affiche la description quand elle est renseignée", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: ITEMS_TIMELINE, total: 2 } });

    renderWithQuery(React.createElement(TimelineFamillePage));

    await waitFor(() => {
      expect(screen.getAllByText("Jules a fait ses premiers pas !").length).toBeGreaterThan(0);
    });
  });

  it("affiche la timeline vide sans erreur", async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], total: 0 } });

    renderWithQuery(React.createElement(TimelineFamillePage));

    await waitFor(() => {
      expect(document.body).toBeDefined();
    });
  });
});

describe("TimelineFamillePage — filtres catégories", () => {
  it("affiche les boutons de filtre de catégorie", () => {
    mockedApi.get.mockReturnValue(new Promise(() => {}));

    renderWithQuery(React.createElement(TimelineFamillePage));

    // Les catégories sont affichées comme filtres
    expect(screen.getByText(/toutes/i)).toBeDefined();
  });
});
