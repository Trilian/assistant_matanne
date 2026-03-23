import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
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
  contrats_actifs: 5,
  diagnostics_expires: 0,
  garanties_expirant_bientot: 2,
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: mockStats,
    isLoading: false,
    error: null,
  }),
}));

describe("PageMaison (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Maison", () => {
    render(<PageMaison />);
    expect(screen.getByText(/Maison/)).toBeInTheDocument();
  });

  it("affiche les stats récapitulatives", () => {
    render(<PageMaison />);
    expect(screen.getByText("Projets en cours")).toBeInTheDocument();
    expect(screen.getByText("Tâches en retard")).toBeInTheDocument();
    expect(screen.getByText("Dépenses du mois")).toBeInTheDocument();
    expect(screen.getByText("Contrats actifs")).toBeInTheDocument();
  });

  it("affiche les sections maison", () => {
    render(<PageMaison />);
    expect(screen.getByText("Projets")).toBeInTheDocument();
    expect(screen.getByText("Entretien")).toBeInTheDocument();
    expect(screen.getByText("Jardin")).toBeInTheDocument();
  });

  it("rend les liens vers les sous-pages", () => {
    render(<PageMaison />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/maison/projets");
    expect(hrefs).toContain("/maison/entretien");
    expect(hrefs).toContain("/maison/jardin");
  });
});
