import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageCuisine from "@/app/(app)/cuisine/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: {
      repas_aujourd_hui: [{ type_repas: "dejeuner", recette_nom: "Pâtes" }],
      repas_semaine_count: 5,
      repas_consommes_semaine: 2,
      nb_recettes: 42,
      articles_courses_restants: 3,
      score_anti_gaspillage: 88,
      alertes_inventaire: 1,
      repas_jules_aujourd_hui: [
        {
          type_repas: "dejeuner",
          plat_jules: "Purée de carottes",
          adaptation_auto: true,
          notes_jules: "Version sans sel et texture lisse.",
        },
      ],
      batch_en_cours: true,
      batch_session_id: 12,
    },
    isLoading: false,
    error: null,
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

describe("PageCuisine (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre et les cartes de pilotage", () => {
    render(<PageCuisine />);
    expect(screen.getByRole("heading", { name: /Cuisine/ })).toBeInTheDocument();
    expect(screen.getByText("Repas aujourd'hui")).toBeInTheDocument();
    expect(screen.getByText("Articles à acheter")).toBeInTheDocument();
    expect(screen.getByText("Anti-gaspillage")).toBeInTheDocument();
    expect(screen.getByText("Alertes stock")).toBeInTheDocument();
    expect(screen.getByText("88%")).toBeInTheDocument();
  });

  it("affiche la progression hebdomadaire et le badge de batch en cours", () => {
    render(<PageCuisine />);
    expect(screen.getByText("Progression de la semaine")).toBeInTheDocument();
    expect(screen.getByText("2 / 5 repas consommés")).toBeInTheDocument();
    expect(screen.getByText("40%")).toBeInTheDocument();
    expect(screen.getByText(/42 recettes en bibliothèque/)).toBeInTheDocument();
    expect(screen.getAllByText("En cours").length).toBeGreaterThan(0);
    expect(screen.getByText(/Batch en cours/)).toBeInTheDocument();
  });

  it("affiche la carte Jules avec adaptation automatique et notes", () => {
    render(<PageCuisine />);
    expect(screen.getByText("Menu Jules aujourd'hui")).toBeInTheDocument();
    expect(screen.getByText("Purée de carottes")).toBeInTheDocument();
    expect(screen.getByText("Auto")).toBeInTheDocument();
    expect(screen.getByText("Version sans sel et texture lisse.")).toBeInTheDocument();
  });

  it("rend les liens vers les sous-pages du hub", () => {
    render(<PageCuisine />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/cuisine/recettes");
    expect(hrefs).toContain("/cuisine/ma-semaine");
    expect(hrefs).toContain("/cuisine/courses");
    expect(hrefs).toContain("/cuisine/inventaire");
    expect(hrefs).toContain("/cuisine/batch-cooking");
  });
});
