import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import DashboardPage from "@/app/(app)/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { nom: "Anne" }, isAuthenticated: true }),
}));

const mockTableauBord = {
  repas_aujourd_hui: [{ type_repas: "dejeuner", recette_nom: "Salade" }],
  articles_courses_restants: 5,
  activites_semaine: 3,
  taches_entretien_urgentes: 1,
  suggestion_diner: "Poulet rôti aux légumes",
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key[0] === "tableau-bord") return { data: mockTableauBord, isLoading: false, error: null };
    if (key[0] === "depenses") {
      return {
        data: {
          total_mois: 240,
          delta_mois_precedent: 10,
          total_annee: 1800,
          moyenne_mensuelle: 150,
          par_categorie: { courses: 120, entretien: 80, energie: 40 },
        },
        isLoading: false,
        error: null,
      };
    }
    if (key[0] === "rappels") return { data: { total: 0, rappels: [] }, isLoading: false, error: null };
    if (key[0] === "bilan-mensuel") {
      return {
        data: {
          donnees: {
            depenses: { total: 240 },
            repas: { total_planifies: 12 },
            activites: { total: 4 },
          },
          synthese_ia: "Tout est sous contrôle.",
        },
        isLoading: false,
        error: null,
      };
    }
    if (key[0] === "dashboard" && key[1] === "config") {
      return { data: { config_dashboard: {} }, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "alertes-contextuelles") {
      return { data: { total: 0, items: [] }, isLoading: false, error: null };
    }
    if (key[0] === "dashboard" && key[1] === "points-famille") {
      return {
        data: {
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
        },
        isLoading: false,
        error: null,
      };
    }
    if (key[0] === "dashboard" && key[1] === "score-bienetre") {
      return {
        data: {
          score_global: 68,
          diversite_alimentaire: 70,
          score_nutri: 65,
          activites_sport: 69,
          trend_semaine_precedente: 3,
          periode: { debut: "2026-01-01", fin: "2026-01-07" },
        },
        isLoading: false,
        error: null,
      };
    }
    if (key[0] === "dashboard" && key[1] === "score-ecologique") {
      return {
        data: {
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
        },
        isLoading: false,
        error: null,
      };
    }
    if (key[0] === "famille") {
      return { data: { total: 0, items: [] }, isLoading: false, error: null };
    }
    return { data: null, isLoading: false, error: null };
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
});
