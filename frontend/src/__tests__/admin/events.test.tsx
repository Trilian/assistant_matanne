import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn(() => ({
    data: {
      metriques: { total: 1 },
      items: [
        {
          event_id: "evt-1",
          type: "stock.modifie",
          source: "tests",
          timestamp: "2026-04-02T12:00:00",
          data: { article_id: 7 },
        },
      ],
      total: 1,
    },
    isLoading: false,
    refetch: vi.fn().mockResolvedValue(undefined),
  })),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  declencherEvenementAdmin: vi.fn(),
  lireEvenementsAdmin: vi.fn(),
  rejouerEvenementAdmin: vi.fn(),
  lancerTestE2EOneClickAdmin: vi.fn(),
}));

import {
  declencherEvenementAdmin,
  lancerTestE2EOneClickAdmin,
  rejouerEvenementAdmin,
} from "@/bibliotheque/api/admin";
import PageAdminEvents from "@/app/(app)/admin/events/page";

const mockedDeclencher = vi.mocked(declencherEvenementAdmin);
const mockedRejouer = vi.mocked(rejouerEvenementAdmin);
const mockedOneClick = vi.mocked(lancerTestE2EOneClickAdmin);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

describe("PageAdminEvents", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedDeclencher.mockResolvedValue({
      status: "ok",
      type_evenement: "planning.genere",
      handlers_notifies: 2,
    });
    mockedRejouer.mockResolvedValue({
      status: "ok",
      replayes: [{ event_id: "evt-1", type: "stock.modifie", handlers_notifies: 1 }],
      total: 1,
      handlers_notifies: 1,
    });
    mockedOneClick.mockResolvedValue({
      status: "ok",
      workflow: "one_click",
      user_id: "admin",
      mode: "dry_run",
      total_etapes: 5,
      etapes: [],
    });
  });

  it("declenche un evenement admin depuis le formulaire", async () => {
    renderWithQuery(React.createElement(PageAdminEvents));

    fireEvent.change(screen.getByLabelText(/type d'evenement/i), {
      target: { value: "planning.genere" },
    });
    fireEvent.change(screen.getByLabelText(/payload json/i), {
      target: { value: '{"planning_id":42}' },
    });

    fireEvent.click(screen.getByRole("button", { name: /^emettre$/i }));

    await waitFor(() => {
      expect(mockedDeclencher).toHaveBeenCalledWith({
        type_evenement: "planning.genere",
        source: "admin",
        payload: { planning_id: 42 },
      });
    });
  });

  it("rejoue un evenement depuis l'historique", async () => {
    renderWithQuery(React.createElement(PageAdminEvents));

    fireEvent.click(screen.getByRole("button", { name: /rejouer/i }));

    await waitFor(() => {
      expect(mockedRejouer).toHaveBeenCalledWith({ event_id: "evt-1", limite: 1 });
    });
  });

  it("lance le test one-click", async () => {
    renderWithQuery(React.createElement(PageAdminEvents));

    fireEvent.click(screen.getByRole("button", { name: /lancer test complet/i }));

    await waitFor(() => {
      expect(mockedOneClick).toHaveBeenCalledTimes(1);
    });
  });
});
