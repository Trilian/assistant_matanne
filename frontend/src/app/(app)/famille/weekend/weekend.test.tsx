import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageWeekend from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/weekend",
}));

const mockActivites = [
  { id: 1, titre: "Parc aventure", date: "2025-01-25", type: "sortie", lieu: "Lyon" },
  { id: 2, titre: "Cinéma", date: "2025-01-26", type: "culture", lieu: "Paris" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockActivites, isLoading: false }),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  listerActivites: vi.fn(),
}));

describe("PageWeekend", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Weekend", () => {
    render(<PageWeekend />);
    expect(screen.getByText(/Weekend/)).toBeInTheDocument();
  });

  it("affiche les activités prévues", () => {
    render(<PageWeekend />);
    expect(screen.getByText("Parc aventure")).toBeInTheDocument();
    expect(screen.getByText("Cinéma")).toBeInTheDocument();
  });

  it("affiche la section Ce week-end", () => {
    render(<PageWeekend />);
    expect(screen.getByText("Ce week-end")).toBeInTheDocument();
  });
});
