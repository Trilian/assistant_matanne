import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import DashboardPage from "@/app/(app)/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

const mockDashboardData = {
  repas_aujourd_hui: ["Déjeuner", "Dîner"],
  articles_courses_restants: 5,
  activites_semaine: 3,
  taches_entretien_urgentes: 1,
  suggestion_diner: "Poulet rôti aux légumes",
};

vi.mock("@/hooks/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { nom: "Anne" }, isAuthenticated: true }),
}));

vi.mock("@/hooks/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: mockDashboardData,
    isLoading: false,
    error: null,
  }),
  utiliserMutation: () => ({ mutate: vi.fn() }),
  utiliserInvalidation: () => vi.fn(),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le message de bienvenue", () => {
    render(<DashboardPage />);
    expect(screen.getByText(/Bonjour.*Anne/)).toBeInTheDocument();
  });

  it("affiche les 4 cartes métriques", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Repas aujourd'hui")).toBeInTheDocument();
    expect(screen.getByText("Articles à acheter")).toBeInTheDocument();
    expect(screen.getByText("Activités semaine")).toBeInTheDocument();
    expect(screen.getByText("Alertes entretien")).toBeInTheDocument();
  });

  it("affiche les boutons d'actions rapides", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Nouvelle recette")).toBeInTheDocument();
    expect(screen.getByText("Liste courses")).toBeInTheDocument();
    expect(screen.getByText("Planning repas")).toBeInTheDocument();
    expect(screen.getByText("Chat IA")).toBeInTheDocument();
  });

  it("affiche la suggestion du soir quand disponible", () => {
    render(<DashboardPage />);
    expect(screen.getByText("Suggestion du soir")).toBeInTheDocument();
    expect(screen.getByText("Poulet rôti aux légumes")).toBeInTheDocument();
  });
});
