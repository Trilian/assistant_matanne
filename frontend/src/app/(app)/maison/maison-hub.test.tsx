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
  diagnostics_expirant: 0,
  stocks_en_alerte: 1,
};

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
          alertes: [],
          taches_jour_detail: [],
          meteo: null,
        },
        isLoading: false,
        error: null,
      };
    }

    if (key.includes("predictives")) {
      return { data: [], isLoading: false, error: null };
    }

    if (key.includes("conseils-ia")) {
      return { data: [], isLoading: false, error: null };
    }

    return { data: null, isLoading: false, error: null };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/crochets/utiliser-synthese-vocale", () => ({
  utiliserSyntheseVocale: () => ({
    estSupporte: false,
    enLecture: false,
    lire: vi.fn(),
    arreter: vi.fn(),
  }),
}));

describe("PageMaison (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Maison", () => {
    render(<PageMaison />);
    expect(screen.getByRole("heading", { name: /Maison/ })).toBeInTheDocument();
  });

  it("affiche les stats récapitulatives", () => {
    render(<PageMaison />);
    expect(screen.getByText("Projets en cours")).toBeInTheDocument();
    expect(screen.getByText("Tâches en retard")).toBeInTheDocument();
    expect(screen.getByText("Dépenses du mois")).toBeInTheDocument();
  });

  it("affiche les sections maison", () => {
    render(<PageMaison />);
    expect(screen.getByText("Travaux")).toBeInTheDocument();
    expect(screen.getByText("Ménage")).toBeInTheDocument();
    expect(screen.getByText("Jardin")).toBeInTheDocument();
  });

  it("rend les liens vers les sous-pages", () => {
    render(<PageMaison />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/maison/travaux");
    expect(hrefs).toContain("/maison/menage");
    expect(hrefs).toContain("/maison/jardin");
  });
});
