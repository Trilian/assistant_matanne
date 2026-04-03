import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("date-fns", () => ({
  format: vi.fn(() => "10:00:00"),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  envoyerNotificationTest: vi.fn(),
  envoyerNotificationTestTousCanaux: vi.fn(),
  listerTemplatesNotifications: vi.fn(async () => ({
    status: "ok",
    templates: { telegram: [], email: [] },
    total: 0,
  })),
  listerQueueNotifications: vi.fn(async () => ({
    items: [],
    total_users_pending: 0,
  })),
  relancerQueueNotifications: vi.fn(),
  supprimerQueueNotifications: vi.fn(),
}));

import {
  envoyerNotificationTest,
  envoyerNotificationTestTousCanaux,
} from "@/bibliotheque/api/admin";
import PageAdminNotifications from "@/app/(app)/admin/notifications/page";

const mockedEnvoyerNotificationTest = vi.mocked(envoyerNotificationTest);
const mockedEnvoyerNotificationTestTousCanaux = vi.mocked(envoyerNotificationTestTousCanaux);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

describe("PageAdminNotifications", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      writable: true,
      value: vi.fn(),
    });
  });

  it("envoie un test mono-canal et affiche le succès", async () => {
    mockedEnvoyerNotificationTest.mockResolvedValue({
      resultats: { ntfy: true },
      message: "Notification de test envoyée.",
    });

    renderWithQuery(React.createElement(PageAdminNotifications));

    fireEvent.change(screen.getByLabelText(/message/i), {
      target: { value: "Message de test admin" },
    });

    fireEvent.click(screen.getByRole("button", { name: /envoyer sur/i }));

    await waitFor(() => {
      expect(mockedEnvoyerNotificationTest).toHaveBeenCalledWith({
        canal: "ntfy",
        message: "Message de test admin",
        titre: "Test Matanne",
      });
    });

    expect(screen.getByText(/notification de test envoyée/i)).toBeInTheDocument();
  });

  it("lance le test multi-canal et affiche le résumé", async () => {
    mockedEnvoyerNotificationTestTousCanaux.mockResolvedValue({
      resultats: { ntfy: true, push: true, email: false, telegram: true },
      canaux_testes: ["ntfy", "push", "email", "telegram"],
      succes: ["ntfy", "push", "telegram"],
      echecs: ["email"],
      message: "Test multi-canal terminé.",
    });

    renderWithQuery(React.createElement(PageAdminNotifications));

    fireEvent.change(screen.getByLabelText(/message/i), {
      target: { value: "Campagne multi-canal" },
    });

    fireEvent.click(screen.getByRole("button", { name: /tester tous les canaux/i }));

    await waitFor(() => {
      expect(mockedEnvoyerNotificationTestTousCanaux).toHaveBeenCalledWith(
        expect.objectContaining({
          message: "Campagne multi-canal",
          titre: "Test Matanne",
          inclure_telegram: true,
        }),
      );
    });

    expect(screen.getByText(/test multi-canal terminé/i)).toBeInTheDocument();
    expect(screen.getByText(/succès: ntfy, push, telegram/i)).toBeInTheDocument();
  });
});