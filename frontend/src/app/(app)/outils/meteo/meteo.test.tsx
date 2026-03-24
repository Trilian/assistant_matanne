import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import MeteoPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/outils/meteo",
}));

describe("MeteoPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it("affiche le titre Météo", () => {
    render(<MeteoPage />);
    expect(screen.getByText(/Météo/i)).toBeInTheDocument();
  });

  it("affiche le champ de recherche ville", () => {
    render(<MeteoPage />);
    // Default city is Paris
    const input = screen.getByDisplayValue("Paris");
    expect(input).toBeInTheDocument();
  });
});
