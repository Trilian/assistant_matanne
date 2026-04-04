import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { OngletCuisine } from "./_composants/onglet-cuisine";
import { OngletDonnees } from "./_composants/onglet-donnees";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/parametres",
}));

vi.mock("next-themes", () => ({
  useTheme: () => ({ theme: "light", setTheme: vi.fn() }),
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
    Object.defineProperty(window.navigator, "serviceWorker", {
      configurable: true,
      writable: true,
      value: {
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        getRegistration: vi.fn().mockResolvedValue(undefined),
        controller: undefined,
      },
    });
    Object.defineProperty(window.navigator, "onLine", {
      configurable: true,
      writable: true,
      value: true,
    });
  });

  it("affiche les préférences cuisine apprises par l'IA", () => {
    render(<OngletCuisine />);

    expect(screen.getByText(/préférences apprises par l'ia/i)).toBeInTheDocument();
    expect(screen.getByText(/poisson/i)).toBeInTheDocument();
  });

  it("affiche le suivi de synchronisation hors ligne dans l'onglet Données", () => {
    render(<OngletDonnees />);

    expect(screen.getByText(/synchronisation hors ligne/i)).toBeInTheDocument();
  });
});
