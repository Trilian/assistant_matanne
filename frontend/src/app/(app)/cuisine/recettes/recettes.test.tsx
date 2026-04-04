import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import RecettesPage from "@/app/(app)/cuisine/recettes/page";

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({ invalidateQueries: vi.fn() }),
  useMutation: () => ({
    mutate: vi.fn(),
    mutateAsync: vi.fn().mockResolvedValue({}),
    isPending: false,
    isError: false,
    error: null,
  }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/recettes",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-delai", () => ({
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
      ingredients: [{ nom: "pommes" }, { nom: "farine" }],
    },
    {
      id: 2,
      nom: "Soupe de légumes",
      description: "Soupe réconfortante",
      categorie: "Entrée",
      difficulte: "Facile",
      temps_preparation: 20,
      portions: 4,
      ingredients: [{ nom: "carottes" }, { nom: "poireaux" }],
    },
  ],
  total: 2,
  page: 1,
  pages: 1,
};

const mockDoublons = {
  items: [
    {
      recette_source: { id: 1, nom: "Tarte aux pommes" },
      recette_proche: { id: 3, nom: "Tarte pommes rapide" },
      score_similarite: 0.88,
      raisons: ["Nom très proche", "Base d'ingrédients similaire"],
    },
  ],
  total: 1,
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (queryKey: unknown) => {
    const key = Array.isArray(queryKey) ? queryKey.join(":") : "";

    if (key.includes("doublons")) {
      return {
        data: mockDoublons,
        isLoading: false,
        error: null,
      };
    }

    if (key.includes("semaine")) {
      return {
        data: [],
        isLoading: false,
        error: null,
      };
    }

    return {
      data: mockRecettes,
      isLoading: false,
      error: null,
    };
  },
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserMutationAvecInvalidation: () => ({ mutate: vi.fn(), isPending: false }),
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

  it("affiche la carte de doublons potentiels", () => {
    render(<RecettesPage />);
    expect(screen.getByText(/Doublons potentiels/i)).toBeInTheDocument();
    expect(screen.getByText(/Tarte pommes rapide/i)).toBeInTheDocument();
  });
});
