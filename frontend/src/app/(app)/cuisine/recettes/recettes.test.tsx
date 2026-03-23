import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import RecettesPage from "@/app/(app)/cuisine/recettes/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/recettes",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/hooks/utiliser-delai", () => ({
  utiliserDelai: (value: string) => value,
}));

const mockRecettes = {
  items: [
    {
      id: 1,
      nom: "Tarte aux pommes",
      description: "Une délicieuse tarte",
      categorie: "Dessert",
      difficulte: "Facile",
      temps_preparation: 30,
      portions: 6,
      note_moyenne: 4.5,
    },
    {
      id: 2,
      nom: "Soupe de légumes",
      description: "Soupe réconfortante",
      categorie: "Entrée",
      difficulte: "Facile",
      temps_preparation: 20,
      portions: 4,
      note_moyenne: 4.0,
    },
  ],
  total: 2,
  page: 1,
  pages: 1,
};

vi.mock("@/hooks/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: mockRecettes,
    isLoading: false,
    error: null,
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("RecettesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre principal", () => {
    render(<RecettesPage />);
    expect(screen.getByText(/Recettes/)).toBeInTheDocument();
  });

  it("affiche le champ de recherche", () => {
    render(<RecettesPage />);
    expect(screen.getByPlaceholderText(/Rechercher une recette/i)).toBeInTheDocument();
  });

  it("affiche le nombre de recettes", () => {
    render(<RecettesPage />);
    expect(screen.getByText(/2 recettes/)).toBeInTheDocument();
  });

  it("affiche les noms des recettes", () => {
    render(<RecettesPage />);
    expect(screen.getByText("Tarte aux pommes")).toBeInTheDocument();
    expect(screen.getByText("Soupe de légumes")).toBeInTheDocument();
  });

  it("affiche le bouton Nouvelle recette", () => {
    render(<RecettesPage />);
    expect(screen.getByText("Nouvelle recette")).toBeInTheDocument();
  });

  it("contient le filtre catégorie", () => {
    render(<RecettesPage />);
    expect(screen.getByText("Toutes")).toBeInTheDocument();
  });
});
