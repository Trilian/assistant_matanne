import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import JulesPage from "@/app/(app)/famille/jules/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/jules",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockJalons = [
  {
    id: 1,
    titre: "Premiers pas",
    categorie: "motricite",
    description: "A marché seul pour la première fois",
    age_mois: 12,
    date_observation: "2024-06-15",
  },
  {
    id: 2,
    titre: "Premier mot",
    categorie: "langage",
    description: "A dit maman",
    age_mois: 10,
    date_observation: "2024-04-15",
  },
];

const mockProfil = {
  date_naissance: "2023-06-01",
  prenom: "Jules",
};

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("profil")) {
      return { data: mockProfil, isLoading: false, error: null };
    }
    return { data: mockJalons, isLoading: false, error: null };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("JulesPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre Jules", () => {
    render(<JulesPage />);
    expect(screen.getByRole("heading", { name: /Jules/ })).toBeInTheDocument();
  });

  it("affiche les catégories de filtre", () => {
    render(<JulesPage />);
    expect(screen.getByText("Motricité")).toBeInTheDocument();
    expect(screen.getByText("Langage")).toBeInTheDocument();
    expect(screen.getByText("Cognitif")).toBeInTheDocument();
    expect(screen.getByText("Social")).toBeInTheDocument();
  });

  it("affiche le bouton Nouveau jalon", () => {
    render(<JulesPage />);
    expect(screen.getByText("Nouveau jalon")).toBeInTheDocument();
  });

  it("affiche les jalons enregistrés", () => {
    render(<JulesPage />);
    expect(screen.getByText("Premiers pas")).toBeInTheDocument();
    expect(screen.getByText("Premier mot")).toBeInTheDocument();
  });
});
