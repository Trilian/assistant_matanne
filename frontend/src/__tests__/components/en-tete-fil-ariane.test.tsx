import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { EnTete } from "@/composants/disposition/en-tete";
import { FilAriane } from "@/composants/disposition/fil-ariane";

const mockSetTheme = vi.fn();
const mockBasculerRecherche = vi.fn();
const mockDeconnecter = vi.fn();
const mockLireModeMaintenancePublic = vi.fn();

let mockPathname = "/cuisine/recettes/42";
let mockTitrePage = "Gratin dauphinois";

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
}));

vi.mock("next-themes", () => ({
  useTheme: () => ({
    theme: "dark",
    setTheme: mockSetTheme,
  }),
}));

vi.mock("@/magasins/store-ui", () => ({
  utiliserStoreUI: () => ({
    basculerRecherche: mockBasculerRecherche,
    titrePage: mockTitrePage,
  }),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({
    utilisateur: {
      nom: "Marie Curie",
      email: "marie@example.com",
    },
    deconnecter: mockDeconnecter,
  }),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  lireModeMaintenancePublic: (...args: unknown[]) => mockLireModeMaintenancePublic(...args),
}));

vi.mock("@/composants/disposition/bouton-epingler", () => ({
  BoutonEpingler: () => <button type="button">Épingler</button>,
}));

describe("EnTete", () => {
  beforeEach(() => {
    mockPathname = "/cuisine/recettes/42";
    mockTitrePage = "Gratin dauphinois";
    mockLireModeMaintenancePublic.mockResolvedValue({ maintenance_mode: false });
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("affiche le bandeau maintenance quand le mode public est activé", async () => {
    mockLireModeMaintenancePublic.mockResolvedValue({ maintenance_mode: true });

    render(<EnTete />);

    expect(await screen.findByText(/Maintenance en cours/i)).toBeInTheDocument();
  });

  it("ouvre la recherche, bascule le thème, expose le menu profil et affiche le module actif", async () => {
    render(<EnTete />);

    fireEvent.click(screen.getAllByRole("button", { name: /rechercher/i })[0]);
    expect(mockBasculerRecherche).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: /passer en mode clair/i }));
    expect(mockSetTheme).toHaveBeenCalledWith("light");

    expect(screen.getByRole("button", { name: /mon profil/i })).toBeInTheDocument();
    expect(screen.getByText("MC")).toBeInTheDocument();
    expect(screen.getByText("Module Cuisine")).toBeInTheDocument();
    expect(mockDeconnecter).not.toHaveBeenCalled();
  });
});

describe("FilAriane", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("traduit les segments de l'URL, remplace un identifiant dynamique et affiche le module actif", () => {
    mockPathname = "/cuisine/recettes/42";
    mockTitrePage = "Gratin dauphinois";

    render(<FilAriane />);

    expect(screen.getByLabelText("Accueil")).toBeInTheDocument();
    expect(screen.getByText("Cuisine")).toBeInTheDocument();
    expect(screen.getByText("Recettes")).toBeInTheDocument();
    expect(screen.getByText("Gratin dauphinois")).toBeInTheDocument();
    expect(screen.getByText("Module actif : Cuisine")).toBeInTheDocument();
    expect(screen.queryByText("42")).not.toBeInTheDocument();
  });

  it("reste masqué sur la page d'accueil", () => {
    mockPathname = "/";

    const { container } = render(<FilAriane />);

    expect(container).toBeEmptyDOMElement();
  });
});
