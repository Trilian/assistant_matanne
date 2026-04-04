import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PagePlanningRepas from "./page";

const mockPlanifierSuppression = vi.fn();
const dateRepasTest = (() => {
  const now = new Date();
  const jour = now.getDay();
  const diff = jour === 0 ? -6 : 1 - jour;
  const lundi = new Date(now);
  lundi.setDate(now.getDate() + diff);
  return lundi.toISOString().split("T")[0];
})();

vi.mock("@/composants/planning/calendrier-mensuel", () => ({
  CalendrierMensuel: ({ mois }: { mois: string }) => (
    <div data-testid="calendrier-mensuel">Mois: {mois}</div>
  ),
}));

vi.mock("@/composants/planning/calendrier-mosaique-repas", () => ({
  CalendrierMosaiqueRepas: () => <div data-testid="calendrier-mosaique" />,
}));

vi.mock("@/composants/planning/calendrier-colonnes-planning", () => ({
  CalendrierColonnesPlanning: () => <div data-testid="calendrier-colonnes" />,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/planning",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key[0] === "famille") return { data: [], isLoading: false };
    if (key[0] === "calendriers") return { data: [], isLoading: false };
    if (key[0] === "planning" && key[1] === "mensuel") {
      return { data: { mois: "2026-04", par_jour: {} }, isLoading: false };
    }
    if (key[0] === "planning" && key[1] === "nutrition") {
      return { data: null, isLoading: false };
    }
    if (key[0] === "planning" && key[1] === "conflits") {
      return { data: null, isLoading: false };
    }
    if (key[0] === "planning" && key[1] === "suggestions") {
      return { data: [], isLoading: false };
    }
    return {
      data: {
        repas: [
          {
            id: 42,
            date: dateRepasTest,
            date_repas: dateRepasTest,
            type_repas: "diner",
            recette_nom: "Lasagnes maison",
            notes: "Lasagnes maison",
            portions: 4,
            nutri_score: "b",
          },
        ],
      },
      isLoading: false,
    };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/crochets/utiliser-suppression-annulable", () => ({
  utiliserSuppressionAnnulable: () => ({ planifierSuppression: mockPlanifierSuppression }),
}));

vi.mock("@/bibliotheque/api/planning", () => ({
  obtenirPlanningSemaine: vi.fn(),
  obtenirPlanningMensuel: vi.fn(),
  obtenirConflitsPlanning: vi.fn(),
  definirRepas: vi.fn(),
  supprimerRepas: vi.fn(),
  genererPlanningSemaine: vi.fn(),
  exporterPlanningIcal: vi.fn(),
  exporterPlanningPdf: vi.fn(),
  obtenirNutritionHebdo: vi.fn(),
  obtenirSuggestionsRapides: vi.fn(),
}));

vi.mock("@/bibliotheque/api/courses", () => ({
  genererCoursesDepuisPlanning: vi.fn(),
}));

vi.mock("@/bibliotheque/api/batch-cooking", () => ({
  genererSessionDepuisPlanning: vi.fn(),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerEvenementsFamiliaux: vi.fn(),
}));

vi.mock("@/bibliotheque/api/calendriers", () => ({
  listerEvenements: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PagePlanningRepas", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Planning Repas", () => {
    renderWithQuery(<PagePlanningRepas />);
    expect(screen.getByRole("heading", { name: /planning repas/i })).toBeInTheDocument();
  });

  it("affiche les jours de la semaine", () => {
    renderWithQuery(<PagePlanningRepas />);
    expect(screen.getByText("Lundi")).toBeInTheDocument();
    expect(screen.getByText("Dimanche")).toBeInTheDocument();
  });

  it("bascule entre vue semaine et vue mois", async () => {
    const user = userEvent.setup();
    renderWithQuery(<PagePlanningRepas />);

    expect(screen.getByText("Lundi")).toBeInTheDocument();
    expect(screen.queryByTestId("calendrier-mensuel")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /^Mois$/i }));
    expect(screen.getByTestId("calendrier-mensuel")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /^Semaine$/i }));
    expect(screen.getByText("Lundi")).toBeInTheDocument();
  });

  it("planifie une suppression annulable lors du retrait d'un repas", async () => {
    const user = userEvent.setup();
    renderWithQuery(<PagePlanningRepas />);

    await user.click(screen.getByRole("button", { name: /retirer le repas/i }));

    expect(mockPlanifierSuppression).toHaveBeenCalledTimes(1);
  });
});
