import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import PageGarmin from "@/app/(app)/famille/garmin/page";

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserInvalidation: () => vi.fn(),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserRequete: (key: unknown) => {
    const valeur = Array.isArray(key) ? key.join(":") : "";

    if (valeur.includes("suggestion-soir")) {
      return {
        data: {
          recommandation: "Balade calme de 20 minutes puis étirements en intérieur",
          raison: "Peu d'activité récente et météo douce en soirée.",
          alternatives: ["Jeu moteur à la maison", "Petite marche après le dîner"],
          niveau_energie: "moderee",
          meteo: "Ciel dégagé",
          temperature_c: 18,
        },
        isLoading: false,
        error: null,
      };
    }

    if (valeur.includes("status")) {
      return {
        data: {
          connected: true,
          display_name: "Profil principal",
          objectif_pas: 8000,
        },
        isLoading: false,
        error: null,
      };
    }

    return {
      data: {
        total_pas: 4200,
        total_calories: 1800,
        total_distance_km: 6.4,
        total_activities: 2,
        streak_jours: 3,
        moyenne_pas_jour: 6000,
        garmin_connected: true,
      },
      isLoading: false,
      error: null,
    };
  },
}));

describe("PageGarmin", () => {
  it("affiche une suggestion d'activité du soir personnalisée", () => {
    render(<PageGarmin />);

    expect(screen.getByText(/Activité du soir recommandée/i)).toBeInTheDocument();
    expect(screen.getByText(/Balade calme de 20 minutes/i)).toBeInTheDocument();
    expect(screen.getByText(/Peu d'activité récente/i)).toBeInTheDocument();
  });
});
