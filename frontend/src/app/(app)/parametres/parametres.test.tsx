import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageParametres from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/parametres",
}));

vi.mock("next-themes", () => ({
  useTheme: () => ({ theme: "light", setTheme: vi.fn() }),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { nom: "Anne", email: "anne@test.com" } }),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: { theme: "light", langue: "fr" }, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: { get: vi.fn(), post: vi.fn(), put: vi.fn() },
}));

vi.mock("@/bibliotheque/api/preferences", () => ({
  obtenirPreferences: vi.fn(),
  sauvegarderPreferences: vi.fn(),
}));

vi.mock("@/bibliotheque/api/push", () => ({
  statutPush: vi.fn(),
  souscrirePush: vi.fn(),
  desabonnerPush: vi.fn(),
}));

describe("PageParametres", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Paramètres", () => {
    render(<PageParametres />);
    expect(screen.getByText(/Paramètres/)).toBeInTheDocument();
  });

  it("affiche les onglets de configuration", () => {
    render(<PageParametres />);
    expect(screen.getByRole("tab", { name: /Profil/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Cuisine/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Notifications/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /Affichage/ })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /IA/ })).toBeInTheDocument();
  });

  it("affiche la description", () => {
    render(<PageParametres />);
    expect(screen.getByText("Configuration de l'application")).toBeInTheDocument();
  });
});
