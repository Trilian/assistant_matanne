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
      repas_aujourd_hui: [{ type_repas: "déjeuner", recette_nom: "Pâtes" }],
      repas_semaine_count: 5,
      nb_recettes: 42,
      articles_courses_restants: 3,
      alertes_inventaire: 1,
      batch_en_cours: false,
      batch_session_id: null,
    },
    isLoading: false,
    error: null,
  }),
}));

describe("PageCuisine (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Cuisine", () => {
    render(<PageCuisine />);
    expect(screen.getByText(/Cuisine/)).toBeInTheDocument();
  });

  it("affiche les 6 sections", () => {
    render(<PageCuisine />);
    expect(screen.getByText("Recettes")).toBeInTheDocument();
    expect(screen.getByText("Planning repas")).toBeInTheDocument();
    expect(screen.getByText("Courses")).toBeInTheDocument();
    expect(screen.getByText("Inventaire")).toBeInTheDocument();
    expect(screen.getByText("Batch Cooking")).toBeInTheDocument();
    expect(screen.getByText("Anti-Gaspillage")).toBeInTheDocument();
  });

  it("affiche les stats du dashboard", () => {
    render(<PageCuisine />);
    expect(screen.getByText("Repas aujourd'hui")).toBeInTheDocument();
    expect(screen.getByText("Articles à acheter")).toBeInTheDocument();
    expect(screen.getByText("Recettes")).toBeInTheDocument();
  });

  it("rend les liens vers les sous-pages", () => {
    render(<PageCuisine />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/cuisine/recettes");
    expect(hrefs).toContain("/cuisine/planning");
    expect(hrefs).toContain("/cuisine/courses");
    expect(hrefs).toContain("/cuisine/inventaire");
  });
});
