import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import HabitatPage from "@/app/(app)/habitat/page";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => <a href={href}>{children}</a>,
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: {
      scenarios: 2,
      annonces: 4,
      plans: 1,
      projets_deco: 3,
      zones_jardin: 5,
      alertes: 1,
      annonces_a_traiter: 2,
      budget_deco_total: 1200,
      budget_deco_depense: 450,
    },
  }),
}));

vi.mock("@/crochets/utiliser-stockage-local", () => ({
  utiliserStockageLocal: () => [
    {
      dateIso: new Date(Date.now() - 26 * 60 * 60 * 1000).toISOString(),
    },
    vi.fn(),
    vi.fn(),
  ],
}));

describe("HabitatPage", () => {
  it("affiche le titre Habitat et les sections principales", () => {
    render(<HabitatPage />);
    expect(screen.getByRole("heading", { name: /^Habitat$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Scenarios/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Veille Immo/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Marche/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Plans/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Deco/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Jardin/i })).toBeInTheDocument();
    expect(screen.getByText(/Derniere sync: A rafraichir/i)).toBeInTheDocument();
  });
});
