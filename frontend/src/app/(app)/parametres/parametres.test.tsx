import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PageParametres from "./page";

const mockSetTheme = vi.fn();
const mockStartViewTransition = vi.fn((callback: () => void) => callback());

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/parametres",
}));

vi.mock("next-themes", () => ({
  useTheme: () => ({ theme: "light", setTheme: mockSetTheme }),
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
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(document, "startViewTransition", {
      configurable: true,
      writable: true,
      value: mockStartViewTransition,
    });
  });

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

  it("affiche l'aperçu en direct du thème et utilise la transition native", async () => {
    const user = userEvent.setup();
    render(<PageParametres />);

    await user.click(screen.getByRole("tab", { name: /Affichage/i }));

    expect(screen.getByText(/aperçu en direct/i)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /^Sombre$/i }));

    expect(mockStartViewTransition).toHaveBeenCalledTimes(1);
    expect(mockSetTheme).toHaveBeenCalledWith("dark");
  });
});
