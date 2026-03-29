// ═══════════════════════════════════════════════════════════
// Tests — Page Outils/Assistant Vocal
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    post: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import AssistantVocalPage from "@/app/(app)/outils/assistant-vocal/page";

const mockedApi = vi.mocked(clientApi);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

beforeEach(() => {
  vi.clearAllMocks();
  // SpeechRecognition n'est pas disponible dans jsdom — on ne tente pas de l'instancier
  Object.defineProperty(window, "SpeechRecognition", {
    value: undefined,
    writable: true,
  });
  Object.defineProperty(window, "webkitSpeechRecognition", {
    value: undefined,
    writable: true,
  });
});

describe("AssistantVocalPage — rendu initial", () => {
  it("affiche le titre de la page", () => {
    renderWithQuery(React.createElement(AssistantVocalPage));
    expect(screen.getByText(/assistant vocal/i)).toBeDefined();
  });

  it("affiche les exemples de commandes", () => {
    renderWithQuery(React.createElement(AssistantVocalPage));
    // Vérifie que des exemples sont rendus en page
    expect(screen.getByText(/Ajoute du lait/i)).toBeDefined();
  });
});

describe("AssistantVocalPage — envoi commande texte", () => {
  it("envoie une commande via le champ texte", async () => {
    mockedApi.post.mockResolvedValue({
      data: { action: "ajouter_article", message: "Lait ajouté à la liste de courses." },
    });

    renderWithQuery(React.createElement(AssistantVocalPage));

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Ajoute du lait" } });

    const submitBtn = screen.getByRole("button", { name: /envoyer/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockedApi.post).toHaveBeenCalled();
    });
  });

  it("affiche le résultat dans l'historique", async () => {
    mockedApi.post.mockResolvedValue({
      data: { action: "ajouter_article", message: "Lait ajouté à la liste de courses." },
    });

    renderWithQuery(React.createElement(AssistantVocalPage));

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "Ajoute du lait" } });
    fireEvent.submit(input.closest("form") ?? input);

    await waitFor(() => {
      expect(screen.getByText(/ajouté/i)).toBeDefined();
    });
  });
});
