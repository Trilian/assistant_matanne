import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BankrollWidget } from "./bankroll-widget";

vi.mock("recharts", async () => {
  const actual = await vi.importActual<typeof import("recharts")>("recharts");
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="mock-responsive-container">{children}</div>
    ),
  };
});

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () =>
      Promise.resolve({
        bankroll_actuelle: 1200,
        bankroll_initiale: 1000,
        variation_totale: 200,
        roi: 20.0,
        historique: [],
      }),
  });
});

const wrap = (ui: React.ReactNode) => {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return <QueryClientProvider client={qc}>{ui}</QueryClientProvider>;
};

describe("BankrollWidget", () => {
  it("affiche un skeleton pendant le chargement", () => {
    render(wrap(<BankrollWidget userId={1} />));
    const skeletons = document.querySelectorAll('[data-slot="skeleton"]');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("affiche le titre après chargement", async () => {
    render(wrap(<BankrollWidget userId={1} />));
    const title = await screen.findByText(/Gestion Bankroll/);
    expect(title).toBeDefined();
  });
});
