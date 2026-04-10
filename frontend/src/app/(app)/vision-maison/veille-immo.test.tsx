import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import VeilleImmoHabitatPage from "@/app/(app)/habitat/veille-immo/page";

const mutateAsyncMock = vi.fn();
const setSourcesMock = vi.fn();
const setDerniereSyncMock = vi.fn();
const resetDerniereSyncMock = vi.fn();
let derniereSyncMock = {
  dateIso: "2026-03-28T08:00:00.000Z",
  limiteParSource: 10,
  sources: ["leboncoin", "bienici"],
  annoncesCreees: 5,
  annoncesMisesAJour: 2,
  alertes: 1,
};

vi.mock("next/dynamic", () => ({
  default: () => () => <div data-testid="mock-carte-leaflet" />,
}));

vi.mock("@/crochets/utiliser-stockage-local", () => ({
  utiliserStockageLocal: (key: string) => {
    if (key === "habitat.veille.sources") {
      return [["leboncoin", "bienici", "seloger", "pap"], setSourcesMock, vi.fn()];
    }
    return [derniereSyncMock, setDerniereSyncMock, resetDerniereSyncMock];
  },
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key[2] === "annonces") {
      return {
        data: [
          {
            id: 1,
            source: "leboncoin",
            url_source: "https://example.com/1",
            titre: "Maison proche lac",
            prix: 520000,
            surface_m2: 120,
            nb_pieces: 5,
            statut: "alerte",
            score_pertinence: 0.9,
            ecart_prix_pct: -8,
          },
        ],
      };
    }
    if (key[2] === "alertes") {
      return {
        data: [
          {
            source: "leboncoin",
            url_source: "https://example.com/1",
            titre: "Maison proche lac",
            score: 0.91,
            ville: "Annecy",
            prix: 520000,
          },
        ],
      };
    }
    if (key[2] === "carte") {
      return {
        data: [
          {
            ville: "Annecy",
            code_postal: "74000",
            nb_annonces: 3,
            score_max: 0.91,
            latitude: 45.9,
            longitude: 6.1,
          },
        ],
      };
    }
    return { data: [] };
  },
  utiliserMutationAvecInvalidation: () => ({
    mutateAsync: mutateAsyncMock,
    isPending: false,
    data: {
      stats_sources: [{ source: "leboncoin", url: "https://example.com", annonces: 6, alertes: 2 }],
    },
  }),
}));

describe("VeilleImmoHabitatPage", () => {
  beforeEach(() => {
    mutateAsyncMock.mockReset();
    setSourcesMock.mockReset();
    setDerniereSyncMock.mockReset();
    resetDerniereSyncMock.mockReset();
    derniereSyncMock = {
      dateIso: "2026-03-28T08:00:00.000Z",
      limiteParSource: 10,
      sources: ["leboncoin", "bienici"],
      annoncesCreees: 5,
      annoncesMisesAJour: 2,
      alertes: 1,
    };
    mutateAsyncMock.mockResolvedValue({
      annonces_creees: 4,
      annonces_mises_a_jour: 3,
      alertes: 2,
      stats_sources: [{ source: "leboncoin", url: "https://example.com", annonces: 6, alertes: 2 }],
    });
  });

  it("envoie les sources selectionnees lors de la synchronisation", async () => {
    render(<VeilleImmoHabitatPage />);

    fireEvent.click(screen.getByRole("button", { name: /Synchroniser/i }));

    await waitFor(() => {
      expect(mutateAsyncMock).toHaveBeenCalledWith({
        limite_par_source: 10,
        sources: ["leboncoin", "bienici", "seloger", "pap"],
      });
    });
  });

  it("sauvegarde le resume de la derniere sync", async () => {
    render(<VeilleImmoHabitatPage />);

    fireEvent.click(screen.getByRole("button", { name: /Synchroniser/i }));

    await waitFor(() => {
      expect(setDerniereSyncMock).toHaveBeenCalled();
    });
  });

  it("affiche un indicateur stale et permet d'effacer l'historique local", () => {
    render(<VeilleImmoHabitatPage />);

    expect(screen.getByText(/A rafraichir/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Effacer l'historique local/i }));
    expect(resetDerniereSyncMock).toHaveBeenCalled();
  });

  it("affiche un indicateur ambre entre 12h et 24h", () => {
    derniereSyncMock = {
      dateIso: new Date(Date.now() - 15 * 60 * 60 * 1000).toISOString(),
      limiteParSource: 10,
      sources: ["leboncoin", "bienici"],
      annoncesCreees: 3,
      annoncesMisesAJour: 1,
      alertes: 0,
    };

    render(<VeilleImmoHabitatPage />);

    expect(screen.getByText(/A surveiller \(12-24h\)/i)).toBeInTheDocument();
  });

  it("affiche la section de couverture et les toggles de source", () => {
    render(<VeilleImmoHabitatPage />);

    expect(screen.getByText(/Couverture par source/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /leboncoin/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /bienici/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /seloger/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /pap/i })).toBeInTheDocument();
  });
});
