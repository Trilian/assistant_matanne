import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import PageMaison from "@/app/(app)/maison/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockStats = {
  projets_en_cours: 3,
  taches_en_retard: 1,
  depenses_mois: 450.5,
  diagnostics_expirant: 0,
  stocks_en_alerte: 1,
};

const mockEnvoyerRappels = vi.fn();
const mockLire = vi.fn();
const mockArreter = vi.fn();

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (queryKey: unknown) => {
    const key = Array.isArray(queryKey) ? queryKey.join(":") : "";

    if (key.includes("stats")) {
      return { data: mockStats, isLoading: false, error: null };
    }

    if (key.includes("briefing")) {
      return {
        data: {
          resume: "Briefing maison",
          alertes: [
            {
              niveau: "CRITIQUE",
              titre: "Chaudière",
              message: "Contrôle annuel à planifier",
              action_url: "/maison/documents",
            },
            {
              niveau: "BASSE",
              titre: "Poubelles",
              message: "Sortir le tri demain",
            },
          ],
          taches_jour_detail: [
            { nom: "Aérer le salon", fait: false, duree_estimee_min: 10 },
            { nom: "Vérifier le jardin", fait: true, duree_estimee_min: 5 },
          ],
          meteo: {
            temperature_min: 9,
            temperature_max: 16,
            description: "Pluie faible",
            impact_jardin: "Reporter l'arrosage automatique.",
            alertes_meteo: ["Vent"],
          },
          jardin: [],
          cellier_alertes: [],
        },
        isLoading: false,
        error: null,
      };
    }

    if (key.includes("conseils-ia")) {
      return { data: [], isLoading: false, error: null };
    }

    return { data: null, isLoading: false, error: null };
  },
  utiliserMutation: () => ({ mutate: mockEnvoyerRappels, isPending: false }),
}));

vi.mock("@/crochets/utiliser-synthese-vocale", () => ({
  utiliserSyntheseVocale: () => ({
    estSupporte: true,
    enLecture: true,
    lire: mockLire,
    arreter: mockArreter,
  }),
}));

describe("PageMaison (Hub)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre, le briefing et les stats récapitulatives", () => {
    render(<PageMaison />);
    expect(screen.getByRole("heading", { name: /Maison/ })).toBeInTheDocument();
    expect(screen.getByText("Briefing maison")).toBeInTheDocument();
    expect(screen.getByText("Projets en cours")).toBeInTheDocument();
    expect(screen.getByText("Tâches en retard")).toBeInTheDocument();
    expect(screen.getByText("451 €")).toBeInTheDocument();
  });

  it("affiche les blocs contextuels du jour et les liens majeurs", () => {
    render(<PageMaison />);
    expect(screen.getByText(/Aujourd'hui \(1 tâche\)/)).toBeInTheDocument();
    expect(screen.getByText(/Alertes urgentes \(1\)/)).toBeInTheDocument();
    expect(screen.getByText("Reporter l'arrosage automatique.")).toBeInTheDocument();
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/maison/travaux");
    expect(hrefs).toContain("/maison/menage");
    expect(hrefs).toContain("/maison/jardin");
    expect(hrefs).toContain("/maison/visualisation");
  });

  it("declenche les rappels push et la lecture vocale du briefing", () => {
    render(<PageMaison />);
    fireEvent.click(screen.getByRole("button", { name: /Rappels push/i }));
    expect(mockEnvoyerRappels).toHaveBeenCalledWith(undefined);

    fireEvent.click(screen.getByRole("button", { name: /Lire le briefing/i }));
    expect(mockLire).toHaveBeenCalledWith(
      "Briefing maison. Vous avez 1 taches a faire aujourd'hui et 1 alertes urgentes."
    );

    fireEvent.click(screen.getByRole("button", { name: /Arrêter/i }));
    expect(mockArreter).toHaveBeenCalledTimes(1);
  });
});
