import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import PageOutils from "@/app/(app)/outils/page";
import IAAvanceePage from "@/app/(app)/ia-avancee/page";
import PagePlanningRedirect from "@/app/(app)/planning/page";

const redirectMock = vi.fn();

vi.mock("next/navigation", () => ({
  redirect: (url: string) => redirectMock(url),
}));

vi.mock("@/bibliotheque/api/avance", () => ({
  obtenirModePiloteAuto: vi.fn().mockResolvedValue({
    actif: true,
    niveau_autonomie: "validation_requise",
    actions: [],
  }),
  configurerModePiloteAuto: vi.fn().mockResolvedValue({
    actif: true,
    niveau_autonomie: "validation_requise",
    actions: [],
  }),
}));

vi.mock("@/bibliotheque/api/ia_avancee", () => ({
  obtenirPrevisionDepenses: vi.fn().mockResolvedValue({ prevision_fin_mois: 1800 }),
  obtenirRecommandationsEnergie: vi.fn().mockResolvedValue({ recommandations: [{ id: 1 }] }),
  obtenirPredictionPannes: vi.fn().mockResolvedValue({ predictions: [{ id: 1 }] }),
  obtenirSuggestionsProactives: vi
    .fn()
    .mockResolvedValue({ suggestions: [{ titre: "Action", message: "Faire X" }] }),
}));

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

describe("Pages hub", () => {
  it("rend le hub outils", () => {
    renderWithQuery(<PageOutils />);
    expect(screen.getByText("🔧 Outils")).toBeInTheDocument();
    expect(screen.getByText("Chat IA")).toBeInTheDocument();
  });

  it("rend le hub IA avancée", () => {
    renderWithQuery(<IAAvanceePage />);
    expect(screen.getByText("IA Avancée")).toBeInTheDocument();
    expect(screen.getByText("Suggestions achats")).toBeInTheDocument();
  });

  it("redirige /planning vers /cuisine/planning", () => {
    PagePlanningRedirect();
    expect(redirectMock).toHaveBeenCalledWith("/cuisine/planning");
  });
});
