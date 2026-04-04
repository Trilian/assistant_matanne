import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import JardinPage from "@/app/(app)/maison/jardin/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/jardin",
  useSearchParams: () => ({ get: () => null }),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockPlantes = [
  {
    id: 1,
    nom: "Tomates cerises",
    type: "Légume",
    statut: "en_cours",
    location: "Potager",
    date_plantation: "2024-04-15",
  },
  {
    id: 2,
    nom: "Basilic",
    type: "Aromate",
    statut: "recolte",
    location: "Bac",
    date_plantation: "2024-05-01",
  },
];

const mockCalendrier = {
  a_semer: [{ nom: "Radis" }, { nom: "Laitue" }],
  a_planter: [{ nom: "Tomates" }],
  a_recolter: [],
};

const mockCalendrierIA = {
  mois: 4,
  region: "Maison",
  meteo_resume: {
    temp_moy_max: 19,
    temp_moy_min: 8,
    pluie_7j_mm: 12,
    suggestions_meteo: ["Temps doux pour les semis"],
  },
  a_semer: [{ nom: "Carottes" }],
  a_planter: [{ nom: "Tomates" }],
  a_recolter: [{ nom: "Radis" }],
  conseils_personnalises: ["Conditions favorables pour lancer les semis ce week-end."],
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("calendrier-personnalise")) {
      return { data: mockCalendrierIA, isLoading: false, error: null };
    }
    if (key.includes("semis")) {
      return { data: mockCalendrier, isLoading: false, error: null };
    }
    return { data: mockPlantes, isLoading: false, error: null };
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("JardinPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre Jardin", () => {
    render(<JardinPage />);
    expect(screen.getByText(/Jardin/)).toBeInTheDocument();
  });

  it("affiche les onglets Mes plantes et Calendrier semis", () => {
    render(<JardinPage />);
    expect(screen.getByText("Mes plantes")).toBeInTheDocument();
    expect(screen.getByText("Calendrier semis")).toBeInTheDocument();
  });

  it("affiche les plantes enregistrées", () => {
    render(<JardinPage />);
    expect(screen.getAllByText("Tomates cerises").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Basilic").length).toBeGreaterThan(0);
  });

  it("affiche la description du jardin", () => {
    render(<JardinPage />);
    expect(screen.getByText(/calendrier des semis/)).toBeInTheDocument();
  });

  it("affiche la vision IA locale pour les semis et récoltes", () => {
    render(<JardinPage />);
    expect(screen.getByText(/Vision IA locale/i)).toBeInTheDocument();
    expect(screen.getByText(/Conditions favorables pour lancer les semis/i)).toBeInTheDocument();
  });
});
