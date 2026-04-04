import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PageParametres from "./page";

const mockSetTheme = vi.fn();
const mockStartViewTransition = vi.fn((callback: () => void) => callback());

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/parametres",
}));

vi.mock("next-themes", () => ({
  useTheme: () => ({ theme: "light", setTheme: mockSetTheme }),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { nom: "Anne", email: "anne@test.com" } }),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key[0] === "preferences" && key[1] === "apprentissage-habitudes") {
      return {
        data: {
          habitudes_detectees: ["Le poisson fonctionne bien le mardi", "Les repas express sont privilégiés en semaine"],
          ajustements_systeme: ["Réduire les recettes souvent reportées"],
          niveau_confiance: 0.72,
        },
        isLoading: false,
      };
    }
    if (key[0] === "preferences" && key[1] === "apprises") {
      return {
        data: {
          semaines_analysees: 3,
          influence_active: true,
          preferences_favorites: [{ categorie: "categorie_recette", valeur: "poisson", score_confiance: 0.82 }],
          preferences_a_eviter: [],
          ajustements_suggestions: ["Prioriser les recettes poisson"],
        },
        isLoading: false,
      };
    }
    if (key[0] === "preferences") {
      return {
        data: {
          nb_adultes: 2,
          jules_present: true,
          jules_age_mois: 19,
          temps_semaine: 30,
          temps_weekend: 60,
          poisson_par_semaine: 2,
          vegetarien_par_semaine: 1,
          viande_rouge_max: 2,
          aliments_exclus: [],
          aliments_favoris: ["pâtes"],
          robots: [],
          magasins_preferes: ["Carrefour"],
        },
        isLoading: false,
      };
    }
    return { data: { theme: "light", langue: "fr" }, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: { get: vi.fn(), post: vi.fn(), put: vi.fn() },
}));

vi.mock("@/bibliotheque/api/preferences", () => ({
  obtenirPreferences: vi.fn(),
  sauvegarderPreferences: vi.fn(),
}));

vi.mock("@/bibliotheque/api/push", () => ({
  statutPush: vi.fn(),
  souscrirePush: vi.fn(),
  desabonnerPush: vi.fn(),
}));

describe("PageParametres", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(document, "startViewTransition", {
      configurable: true,
      writable: true,
      value: mockStartViewTransition,
    });
  });

  it("affiche le titre Paramètres", () => {
    render(<PageParametres />);
    expect(screen.getByText(/Paramètres/)).toBeInTheDocument();
  });

  it("affiche les onglets de configuration", () => {
    render(<PageParametres />);
    expect(screen.getByRole("tab", { name: /Profil/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Cuisine/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Notifications/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Affichage/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /IA/ })).toBeInTheDocument();
  });

  it("affiche la description", () => {
    render(<PageParametres />);
    expect(screen.getByText("Configuration de l'application")).toBeInTheDocument();
  });

  it("affiche l'aperçu en direct du thème et utilise la transition native", async () => {
    const user = userEvent.setup();
    render(<PageParametres />);

    await user.click(screen.getByRole("tab", { name: /Affichage/i }));

    expect(screen.getByText(/aperçu en direct/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /^Sombre$/i }));

    expect(mockStartViewTransition).toHaveBeenCalledTimes(1);
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
  });

  it("affiche les préférences cuisine apprises par l'IA", async () => {
    const user = userEvent.setup();
    render(<PageParametres />);

    await user.click(screen.getByRole("tab", { name: /Cuisine/i }));

    expect(screen.getByText(/préférences apprises par l'ia/i)).toBeInTheDocument();
    expect(screen.getByText(/poisson/i)).toBeInTheDocument();
  });

  it("affiche le suivi de synchronisation hors ligne dans l'onglet Données", async () => {
    const user = userEvent.setup();
    render(<PageParametres />);

    await user.click(screen.getByRole("tab", { name: /Données/i }));

    expect(screen.getByText(/synchronisation hors ligne/i)).toBeInTheDocument();
  });
});
