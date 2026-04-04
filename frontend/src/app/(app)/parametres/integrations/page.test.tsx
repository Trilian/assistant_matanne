import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import IntegrationsPage from "./page";

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (key: string[]) => {
    if (key[0] === "google-calendar") {
      return { data: { connected: false }, isLoading: false };
    }
    return { data: null, isLoading: false };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/calendriers", () => ({
  obtenirUrlAuthGoogle: vi.fn(),
  synchroniserGoogle: vi.fn(),
  statutGoogle: vi.fn(),
  deconnecterGoogle: vi.fn(),
}));

describe("IntegrationsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(window.navigator, "userAgent", {
      configurable: true,
      value: "Mozilla/5.0 Chrome/123.0 Safari/537.36",
    });
    document.documentElement.dataset.assistantMatanneDriveBridge = "";
  });

  it("affiche la section Google Calendar quand le compte n'est pas connecté", () => {
    render(<IntegrationsPage />);

    expect(screen.getByRole("button", { name: /connecter google calendar/i })).toBeInTheDocument();
  });

  it("affiche la carte de configuration de l'extension Chrome quand le bridge est prêt", async () => {
    document.documentElement.dataset.assistantMatanneDriveBridge = "ready";

    render(<IntegrationsPage />);

    expect(screen.getByText(/extension chrome carrefour drive/i)).toBeInTheDocument();
    expect(await screen.findByText(/bridge détecté/i)).toBeInTheDocument();
    expect(screen.getByText(/installation rapide/i)).toBeInTheDocument();
    expect(screen.getByText(/dossier repo/i)).toBeInTheDocument();
  });
});
