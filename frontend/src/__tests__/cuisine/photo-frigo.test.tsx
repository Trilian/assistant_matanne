// ═══════════════════════════════════════════════════════════
// Tests — Page Cuisine/Photo-Frigo (IA multimodal)
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// Mock API client et bibliothèque inventaire
vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: { post: vi.fn(), get: vi.fn() },
}));
vi.mock("@/bibliotheque/api/inventaire", () => ({
  ajouterArticlesBulk: vi.fn(),
}));
vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));

import PhotoFrigoPage from "@/app/(app)/cuisine/photo-frigo/page";

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("PhotoFrigoPage — rendu initial", () => {
  it("affiche le titre de la page", () => {
    renderWithQuery(React.createElement(PhotoFrigoPage));
    expect(screen.getByRole("heading", { name: /Photo Frigo/i })).toBeInTheDocument();
  });

  it("affiche les zones disponibles (frigo, placard, congélateur)", () => {
    renderWithQuery(React.createElement(PhotoFrigoPage));
    expect(screen.getByText("Réfrigérateur")).toBeInTheDocument();
    expect(screen.getByText("Placard")).toBeInTheDocument();
    expect(screen.getByText("Congélateur")).toBeInTheDocument();
  });

  it("affiche le bouton d'upload image", () => {
    renderWithQuery(React.createElement(PhotoFrigoPage));
    // Bouton ou input pour sélectionner une image
    const uploadBtn = document.querySelector('input[type="file"]') || screen.queryByText(/photo/i);
    expect(uploadBtn).not.toBeNull();
  });
});

describe("PhotoFrigoPage — état sans résultat", () => {
  it("n'affiche pas de section recettes quand aucun résultat", () => {
    renderWithQuery(React.createElement(PhotoFrigoPage));
    // Pas de section ingrédients détectés sans résultat
    expect(screen.queryByText(/ingrédients détectés/i)).toBeNull();
  });
});
