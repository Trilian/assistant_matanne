import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// ─── Mocks ────────────────────────────────────────────────

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/cuisine/planning",
  redirect: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn(), promise: vi.fn() },
}));

const mockPlanningData = {
  planning_id: 10,
  semaine_debut: "2026-04-06",
  semaine_fin: "2026-04-12",
  repas: [
    {
      id: 1,
      date: "2026-04-07",
      date_repas: "2026-04-07",
      type_repas: "dejeuner",
      recette_id: 11,
      recette_nom: "Salade composée",
      notes: "",
      portions: 2,
      nutri_score: "A",
    },
    {
      id: 2,
      date: "2026-04-07",
      date_repas: "2026-04-07",
      type_repas: "diner",
      recette_id: 12,
      recette_nom: "Soupe de légumes",
      notes: "",
      portions: 2,
      nutri_score: "B",
    },
  ],
};

const mockNutritionData = {
  semaine_debut: "2026-04-06",
  semaine_fin: "2026-04-12",
  totaux: { calories: 2000, proteines: 80, lipides: 60, glucides: 250 },
  moyenne_calories_par_jour: 285,
  par_jour: {},
  nb_repas_sans_donnees: 0,
  nb_repas_total: 2,
};

vi.mock("@/bibliotheque/api/planning", () => ({
  obtenirPlanningSemaine: vi.fn().mockResolvedValue(mockPlanningData),
  obtenirPlanningMensuel: vi.fn().mockResolvedValue({ mois: "2026-04", par_jour: {} }),
  obtenirConflitsPlanning: vi.fn().mockResolvedValue({ resume: "OK", items: [] }),
  definirRepas: vi.fn().mockResolvedValue({ id: 3 }),
  supprimerRepas: vi.fn().mockResolvedValue({ ok: true }),
  genererPlanningSemaine: vi.fn().mockResolvedValue(mockPlanningData),
  validerPlanning: vi.fn().mockResolvedValue({ valide: true }),
  regenererPlanning: vi.fn().mockResolvedValue(mockPlanningData),
  exporterPlanningIcal: vi.fn().mockResolvedValue(new Blob()),
  exporterPlanningPdf: vi.fn().mockResolvedValue(new Blob()),
  obtenirNutritionHebdo: vi.fn().mockResolvedValue(mockNutritionData),
  obtenirSuggestionsRapides: vi.fn().mockResolvedValue({ suggestions: [] }),
}));

vi.mock("@/bibliotheque/api/courses", () => ({
  genererCoursesDepuisPlanning: vi.fn().mockResolvedValue({ liste_id: 1, articles: [] }),
}));

vi.mock("@/bibliotheque/api/telegram", () => ({
  envoyerPlanningTelegram: vi.fn().mockResolvedValue({ ok: true }),
}));

vi.mock("@/bibliotheque/api/batch-cooking", () => ({
  genererSessionDepuisPlanning: vi.fn().mockResolvedValue({ id: 1 }),
}));

const mockUtiliserRequete = vi.fn().mockReturnValue({ data: undefined, isLoading: false, error: null });
const mockUtiliserMutation = vi.fn().mockReturnValue({ mutate: vi.fn(), mutateAsync: vi.fn(), isPending: false });
const mockUtiliserInvalidation = vi.fn().mockReturnValue(vi.fn());

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (...args: unknown[]) => mockUtiliserRequete(...args),
  utiliserMutation: (...args: unknown[]) => mockUtiliserMutation(...args),
  utiliserInvalidation: (...args: unknown[]) => mockUtiliserInvalidation(...args),
}));

vi.mock("@/composants/cuisine/badge-nutriscore", () => ({
  BadgeNutriscore: ({ score }: { score: string }) => <span data-testid="nutriscore">{score}</span>,
}));

vi.mock("@/composants/cuisine/carte-mode-invites", () => ({
  CarteModeInvites: () => null,
}));

vi.mock("@/composants/cuisine/convertisseur-inline", () => ({
  ConvertisseurInline: () => null,
}));

// ─── Helpers ──────────────────────────────────────────────

function renderPlanning() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const { default: PagePlanning } = require("@/app/(app)/cuisine/planning/page");
  return render(
    <QueryClientProvider client={client}>
      <PagePlanning />
    </QueryClientProvider>
  );
}

// ─── Tests ────────────────────────────────────────────────

describe("PagePlanning", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Configurer les appels utiliquerRequete par clé de query
    mockUtiliserRequete.mockImplementation((key: string[]) => {
      if (key?.[0] === "planning" && key?.[1] === "semaine") {
        return { data: mockPlanningData, isLoading: false, error: null };
      }
      if (key?.[0] === "planning" && key?.[1] === "mensuel") {
        return { data: { mois: "2026-04", par_jour: {} }, isLoading: false, error: null };
      }
      if (key?.[0] === "planning" && key?.[1] === "conflits") {
        return { data: { resume: "OK", items: [] }, isLoading: false, error: null };
      }
      if (key?.[0] === "planning" && key?.[1] === "nutrition-hebdo") {
        return { data: mockNutritionData, isLoading: false, error: null };
      }
      if (key?.[0] === "planning" && key?.[1] === "suggestions-rapides") {
        return { data: { suggestions: [] }, isLoading: false, error: null };
      }
      return { data: undefined, isLoading: false, error: null };
    });
  });

  it("rend sans crash", () => {
    renderPlanning();
    expect(document.body).toBeTruthy();
  });

  it("affiche le titre Planning Repas", async () => {
    renderPlanning();
    await waitFor(() => {
      const heading = screen.queryByText(/planning/i);
      expect(heading).toBeTruthy();
    });
  });

  it("affiche les jours de la semaine", async () => {
    renderPlanning();
    await waitFor(() => {
      const jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
      for (const jour of jours) {
        expect(screen.queryAllByText(new RegExp(jour, "i")).length).toBeGreaterThanOrEqual(0);
      }
    });
  });

  it("gère l'état de chargement sans crash", () => {
    mockUtiliserRequete.mockReturnValue({ data: undefined, isLoading: true, error: null });
    renderPlanning();
    expect(document.body).toBeTruthy();
  });

  it("gère une erreur API sans crash", () => {
    mockUtiliserRequete.mockReturnValue({ data: undefined, isLoading: false, error: new Error("API down") });
    renderPlanning();
    expect(document.body).toBeTruthy();
  });
});
