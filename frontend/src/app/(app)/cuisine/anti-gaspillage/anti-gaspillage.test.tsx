import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageAntiGaspillage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/anti-gaspillage",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockData = {
  score: { score: 85, articles_perimes_mois: 2, articles_sauves_mois: 5, economie_estimee: 25.5 },
  historique: {
    score_moyen_4s: 78,
    tendance: "stable",
    semaines: [
      { debut: "2026-03-01", score: 72 },
      { debut: "2026-03-08", score: 76 },
      { debut: "2026-03-15", score: 80 },
      { debut: "2026-03-22", score: 84 },
    ],
    badges: [],
  },
  articles_urgents: [
    { id: 1, nom: "Yaourts", jours_restants: 1, date_peremption: "2025-01-28" },
    { id: 2, nom: "Salade", jours_restants: 3, date_peremption: "2025-01-30" },
  ],
  recettes_rescue: [
    { id: 1, nom: "Soupe de légumes", temps_total: 20, ingredients_utilises: ["Salade"], difficulte: "facile" },
  ],
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (queryKey: unknown) => {
    const key = Array.isArray(queryKey) ? queryKey.join(":") : "";

    if (key.includes("historique")) {
      return { data: mockData.historique, isLoading: false };
    }

    return { data: mockData, isLoading: false };
  },
}));

vi.mock("@/bibliotheque/api/anti-gaspillage", () => ({
  obtenirAntiGaspillage: vi.fn(),
}));

describe("PageAntiGaspillage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Anti-Gaspillage", () => {
    render(<PageAntiGaspillage />);
    expect(screen.getByText(/Anti-Gaspillage/)).toBeInTheDocument();
  });

  it("affiche le score", () => {
    render(<PageAntiGaspillage />);
    expect(screen.getByText("85")).toBeInTheDocument();
  });

  it("affiche les produits urgents", () => {
    render(<PageAntiGaspillage />);
    expect(screen.getByText("Yaourts")).toBeInTheDocument();
    expect(screen.getAllByText("Salade").length).toBeGreaterThanOrEqual(1);
  });
});
