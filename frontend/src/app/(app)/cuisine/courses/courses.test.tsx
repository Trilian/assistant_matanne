import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageCourses from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/cuisine/courses",
}));

const mockListes = [
  { id: 1, nom: "Courses semaine", nb_articles: 5, nb_coches: 2 },
  { id: 2, nom: "Marché", nb_articles: 3, nb_coches: 0 },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.length === 1 && key[0] === "courses") return { data: mockListes, isLoading: false };
    return { data: null, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/courses", () => ({
  listerListesCourses: vi.fn(),
  obtenirListeCourses: vi.fn(),
  creerListeCourses: vi.fn(),
  ajouterArticle: vi.fn(),
  cocherArticle: vi.fn(),
  supprimerArticle: vi.fn(),
  validerCourses: vi.fn(),
  obtenirSuggestionsBioLocal: vi.fn(),
  obtenirRecurrentsSuggeres: vi.fn(),
  obtenirPredictionsCourses: vi.fn(),
  obtenirQrPartageListe: vi.fn(),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerEvenementsFamiliaux: vi.fn(),
}));

vi.mock("@/bibliotheque/api/calendriers", () => ({
  listerEvenements: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageCourses", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Courses", () => {
    renderWithQuery(<PageCourses />);
    expect(screen.getByRole("heading", { name: /Courses/ })).toBeInTheDocument();
  });

  it("affiche les listes de courses", () => {
    renderWithQuery(<PageCourses />);
    expect(screen.getByText("Courses semaine")).toBeInTheDocument();
    expect(screen.getByText("Marché")).toBeInTheDocument();
  });
});
