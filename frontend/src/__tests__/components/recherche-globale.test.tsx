import { beforeEach, describe, expect, it, vi } from "vitest";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { RechercheGlobale } from "@/composants/disposition/recherche-globale";

const pushMock = vi.fn();
const definirRechercheMock = vi.fn();
const rechercheGlobaleMock = vi.fn();
const toastErrorMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

vi.mock("@/magasins/store-ui", () => ({
  utiliserStoreUI: () => ({
    rechercheOuverte: true,
    definirRecherche: definirRechercheMock,
  }),
}));

vi.mock("@/bibliotheque/api/recherche", () => ({
  rechercheGlobale: (...args: unknown[]) => rechercheGlobaleMock(...args),
}));

vi.mock("sonner", () => ({
  toast: {
    error: (...args: unknown[]) => toastErrorMock(...args),
  },
}));

vi.mock("@/composants/ui/command", () => ({
  CommandDialog: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Command: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CommandInput: ({ value, onValueChange, placeholder }: { value?: string; onValueChange?: (value: string) => void; placeholder?: string }) => (
    <input
      aria-label="recherche"
      placeholder={placeholder}
      value={value ?? ""}
      onChange={(event) => onValueChange?.(event.target.value)}
    />
  ),
  CommandList: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CommandEmpty: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  CommandGroup: ({ heading, children }: { heading?: string; children: React.ReactNode }) => (
    <section>
      <h3>{heading}</h3>
      {children}
    </section>
  ),
  CommandItem: ({ children, onSelect }: { children: React.ReactNode; onSelect?: () => void }) => (
    <button type="button" onClick={() => onSelect?.()}>
      {children}
    </button>
  ),
}));

describe("RechercheGlobale", () => {
  beforeEach(() => {
    vi.useRealTimers();
    pushMock.mockReset();
    definirRechercheMock.mockReset();
    rechercheGlobaleMock.mockReset();
    toastErrorMock.mockReset();
  });

  it("n'appelle pas l'API si la requete a moins de 2 caracteres", async () => {
    render(<RechercheGlobale />);

    fireEvent.change(screen.getByLabelText("recherche"), {
      target: { value: "a" },
    });

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 350));
    });

    await waitFor(() => {
      expect(rechercheGlobaleMock).not.toHaveBeenCalled();
    });
  });

  it("effectue la recherche et affiche les resultats groupes", async () => {
    rechercheGlobaleMock.mockResolvedValue([
      {
        id: 1,
        type: "recette",
        titre: "Gratin dauphinois",
        description: "Pommes de terre creme",
        url: "/cuisine/recettes/1",
      },
      {
        id: 2,
        type: "projet",
        titre: "Refaire la terrasse",
        description: "Printemps",
        url: "/maison/travaux/2",
      },
    ]);

    render(<RechercheGlobale />);

    fireEvent.change(screen.getByLabelText("recherche"), {
      target: { value: "gra" },
    });

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 350));
    });

    await waitFor(() => {
      expect(rechercheGlobaleMock).toHaveBeenCalledWith("gra", 20);
      expect(screen.getByText("Recettes")).toBeInTheDocument();
      expect(screen.getByText("Projets")).toBeInTheDocument();
      expect(screen.getByText("Gratin dauphinois")).toBeInTheDocument();
      expect(screen.getByText("Refaire la terrasse")).toBeInTheDocument();
    });
  });

  it("navigue vers le resultat selectionne", async () => {
    rechercheGlobaleMock.mockResolvedValue([
      {
        id: 7,
        type: "recette",
        titre: "Soupe",
        description: null,
        url: "/cuisine/recettes/7",
      },
    ]);

    render(<RechercheGlobale />);

    fireEvent.change(screen.getByLabelText("recherche"), {
      target: { value: "so" },
    });

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 350));
    });

    await waitFor(() => {
      expect(screen.getByText("Soupe")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("Soupe"));

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 120));
    });

    expect(definirRechercheMock).toHaveBeenCalledWith(false);
    expect(pushMock).toHaveBeenCalledWith("/cuisine/recettes/7");
  });

  it("affiche un toast en cas d'erreur API", async () => {
    rechercheGlobaleMock.mockRejectedValue(new Error("API KO"));

    render(<RechercheGlobale />);

    fireEvent.change(screen.getByLabelText("recherche"), {
      target: { value: "abc" },
    });

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 350));
    });

    await waitFor(() => {
      expect(toastErrorMock).toHaveBeenCalled();
    });
  });
});
