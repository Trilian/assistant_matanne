import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import DashboardPage from "@/app/(app)/page";

const mockEnregistrerActionWidgetDashboard = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/",
  useSearchParams: () => ({ get: vi.fn().mockReturnValue(null) }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { nom: "Anne" }, isAuthenticated: true }),
}));

vi.mock("@/bibliotheque/api/tableau-bord", async () => {
  const actual = await vi.importActual("@/bibliotheque/api/tableau-bord");
  return {
    ...(actual as object),
    enregistrerActionWidgetDashboard: mockEnregistrerActionWidgetDashboard,
  };
});

vi.mock("@/composants/dashboard/grille-dashboard-dnd", () => ({
  GrilleDashboardDnd: ({ children, onWidgetReorder }: { children: React.ReactNode; onWidgetReorder?: (d: { widgetId: string; fromIndex: number; toIndex: number; ordre: string[] }) => void }) => {
    onWidgetReorder?.({ widgetId: "metriques", fromIndex: 0, toIndex: 1, ordre: ["metriques"] });
    return <div>{children}</div>;
  },
  WidgetSortable: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

const mockTableauBord = {
  repas_aujourd_hui: [{ type_repas: "dejeuner", recette_nom: "Salade" }],
  articles_courses_restants: 5,
  activites_semaine: 3,
  taches_entretien_urgentes: 1,
  suggestion_diner: "Poulet rôti aux légumes",
};

const mockDepenses = {
  total_mois: 240,
  delta_mois_precedent: 10,
  total_annee: 1800,
  moyenne_mensuelle: 150,
  par_categorie: { courses: 120, entretien: 80, energie: 40 },
};

const mockBilanMensuel = {
  donnees: {
    depenses: { total: 240 },
    repas: { total_planifies: 12 },
    activites: { total: 4 },
  },
  synthese_ia: "Tout est sous contrôle.",
};

const mockConfigDashboard = { config_dashboard: {} };
const mockAlertesContextuelles = { total: 0, items: [] };
const mockAnomaliesBudget = {
  anomalies: [
    {
      type: "pic",
      categorie: "courses",
      ecart_pourcent: 34,
      severite: "danger",
      description: "Dépenses courses en forte hausse.",
    },
  ],
};
const mockPointsFamille = {
  total_points: 120,
  sport: 40,
  alimentation: 45,
  anti_gaspi: 35,
  badges: ["Bougeotte"],
  details: {
    activites_garmin: 2,
    total_pas: 4000,
    total_calories: 900,
    score_bien_etre: 66,
    articles_a_risque: 1,
  },
};
const mockScoreBienEtre = {
  score_global: 68,
  diversite_alimentaire: 70,
  score_nutri: 65,
  activites_sport: 69,
  trend_semaine_precedente: 3,
  periode: { debut: "2026-01-01", fin: "2026-01-07" },
};
const mockScoreEcologique = {
  score_global: 73,
  niveau: "bon",
  modules: {
    cuisine: { score: 75, anti_gaspillage: 80, produits_ecoscores: 70 },
    maison: {
      score: 70,
      energie: 68,
      eco_actions: 74,
      economie_mensuelle_estimee: 25,
    },
  },
  leviers_prioritaires: ["Réduire les produits proches de péremption."],
};
const mockFamille = { total: 0, items: [] };

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key[0] === "tableau-bord") return { data: mockTableauBord, isLoading: false, error: null };
    if (key[0] === "depenses") {
      return { data: mockDepenses, isLoading: false, error: null };
    }
    if (key[0] === "rappels") return { data: { total: 0, rappels: [] }, isLoading: false, error: null };
    if (key[0] === "bilan-mensuel") {
      return { data: mockBilanMensuel, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "config") {
      return { data: mockConfigDashboard, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "alertes-contextuelles") {
      return { data: mockAlertesContextuelles, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "points-famille") {
      return { data: mockPointsFamille, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "score-bienetre") {
      return { data: mockScoreBienEtre, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "score-ecologique") {
      return { data: mockScoreEcologique, isLoading: false, error: null };
    }
    if (key[0] === "famille" && key[1] === "budget" && key[2] === "anomalies") {
      return { data: mockAnomaliesBudget, isLoading: false, error: null };
    }
    if (key[0] === "famille") {
      return { data: mockFamille, isLoading: false, error: null };
    }
    return { data: null, isLoading: false, error: null };
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockEnregistrerActionWidgetDashboard.mockResolvedValue({ statut: "ok" });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        json: async () => ({}),
      }))
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("affiche le message de bienvenue", () => {
    render(<DashboardPage />);
    expect(screen.getByText(/Bonjour.*Anne/)).toBeInTheDocument();
  });

  it("affiche les cartes metriques", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Repas aujourd'hui")).toBeInTheDocument();
    expect(screen.getByText("Articles à acheter")).toBeInTheDocument();
    expect(screen.getByText("Activités semaine")).toBeInTheDocument();
    expect(screen.getByText("Alertes entretien")).toBeInTheDocument();
  });

  it("affiche les widgets ecologie et suggestion", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Score ecologique")).toBeInTheDocument();
    expect(screen.getByText("Suggestion du soir")).toBeInTheDocument();
    expect(screen.getByText("Poulet rôti aux légumes")).toBeInTheDocument();
  });

  it("affiche le widget alerte budget", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Alerte budget")).toBeInTheDocument();
    expect(screen.getByText("Dépenses courses en forte hausse.")).toBeInTheDocument();
  });

  it("trace le reordonnancement des widgets via action rapide", () => {
    render(<DashboardPage />);
    expect(mockEnregistrerActionWidgetDashboard).toHaveBeenCalledWith(
      expect.objectContaining({
        widget_id: "metriques",
        action: "reordonner_widget",
      })
    );
  });
});
