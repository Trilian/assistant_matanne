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
    },
  }),
}));

describe("HabitatPage", () => {
  it("affiche le titre Habitat et les sections principales", () => {
    render(<HabitatPage />);
    expect(screen.getByText(/Habitat/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Scenarios/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Veille Immo/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Plans/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Deco/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Jardin/i })).toBeInTheDocument();
  });
});
