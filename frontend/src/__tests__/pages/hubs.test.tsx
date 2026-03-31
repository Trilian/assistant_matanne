import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import PageOutils from "@/app/(app)/outils/page";
import IAAvanceePage from "@/app/(app)/ia-avancee/page";
import PagePlanningRedirect from "@/app/(app)/planning/page";

const redirectMock = vi.fn();

vi.mock("next/navigation", () => ({
  redirect: (url: string) => redirectMock(url),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: vi
    .fn()
    .mockReturnValueOnce({ data: { prevision_fin_mois: 1800 } })
    .mockReturnValueOnce({ data: { recommandations: [{ id: 1 }] } })
    .mockReturnValueOnce({ data: { predictions: [{ id: 1 }] } })
    .mockReturnValueOnce({ data: { suggestions: [{ titre: "Action", message: "Faire X" }] } }),
}));

describe("Pages hub", () => {
  it("rend le hub outils", () => {
    render(<PageOutils />);
    expect(screen.getByText("🔧 Outils")).toBeInTheDocument();
    expect(screen.getByText("Chat IA")).toBeInTheDocument();
  });

  it("rend le hub IA avancée", () => {
    render(<IAAvanceePage />);
    expect(screen.getByText("IA Avancée")).toBeInTheDocument();
    expect(screen.getByText("Suggestions achats")).toBeInTheDocument();
  });

  it("redirige /planning vers /cuisine/planning", () => {
    PagePlanningRedirect();
    expect(redirectMock).toHaveBeenCalledWith("/cuisine/planning");
  });
});
