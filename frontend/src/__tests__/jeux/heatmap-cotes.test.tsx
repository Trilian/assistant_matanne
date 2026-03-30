import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HeatmapCotes } from "@/composants/jeux/heatmap-cotes";

vi.mock("next/dynamic", () => ({
  default: (loader: () => unknown) => {
    const MockComponent = ({ children }: { children?: React.ReactNode }) => (
      <div data-testid="dynamic-chart">{children}</div>
    );
    return MockComponent;
  },
}));

describe("HeatmapCotes", () => {
  it("affiche un état vide sans points", () => {
    render(<HeatmapCotes points={[]} matchInfo="PSG vs OM" />);

    expect(screen.getByText(/Aucune donnée d'historique/i)).toBeInTheDocument();
    expect(screen.getByText("PSG vs OM")).toBeInTheDocument();
  });

  it("affiche le résumé des captures avec des points", () => {
    render(
      <HeatmapCotes
        points={[
          {
            timestamp: "2026-03-30T10:00:00Z",
            cote_domicile: 2.1,
            cote_nul: 3.2,
            cote_exterieur: 3.5,
            bookmaker: "Betclic",
          },
        ]}
      />,
    );

    expect(screen.getByText(/captures/i)).toBeInTheDocument();
    expect(screen.getByText(/Source: Betclic/i)).toBeInTheDocument();
  });
});
