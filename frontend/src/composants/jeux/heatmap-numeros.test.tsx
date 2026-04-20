import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { HeatmapNumeros } from "./heatmap-numeros";
import { TooltipProvider } from "@/composants/ui/tooltip";

const wrap = (ui: React.ReactNode) => <TooltipProvider>{ui}</TooltipProvider>;

describe("HeatmapNumeros", () => {
  const frequences = { 1: 10, 2: 5, 3: 20, 4: 15, 5: 1 };

  it("affiche tous les numéros jusqu'à maxNumero", () => {
    render(wrap(<HeatmapNumeros frequences={frequences} maxNumero={5} />));
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByText(String(i))).toBeDefined();
    }
  });

  it("affiche le label", () => {
    render(wrap(<HeatmapNumeros frequences={frequences} maxNumero={5} label="Test Label" />));
    expect(screen.getByText("Test Label")).toBeDefined();
  });

  it("affiche la légende froid/moyen/chaud", () => {
    render(wrap(<HeatmapNumeros frequences={frequences} maxNumero={5} />));
    expect(screen.getByText("Froid")).toBeDefined();
    expect(screen.getByText("Moyen")).toBeDefined();
  });
});
