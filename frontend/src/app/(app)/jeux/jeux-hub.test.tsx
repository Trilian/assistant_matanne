import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageJeux from "@/app/(app)/jeux/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/jeux",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({
    data: {
      value_bets: [],
      opportunites: [],
      loto_retard: [],
      kpis: {
        roi_mois: 12.5,
        taux_reussite_mois: 0.68,
        benefice_mois: 120.5,
        paris_actifs: 5,
      },
    },
    isLoading: false,
    error: null,
  }),
}));

describe("PageJeux (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Jeux", () => {
    render(<PageJeux />);
    expect(screen.getByText(/Jeux/)).toBeInTheDocument();
  });

  it("affiche les 3 sections", () => {
    render(<PageJeux />);
    expect(screen.getByText("Paris")).toBeInTheDocument();
    expect(screen.getByText("Loto")).toBeInTheDocument();
    expect(screen.getByText("Euromillions")).toBeInTheDocument();
  });

  it("affiche les stats paris", () => {
    render(<PageJeux />);
    expect(screen.getByText("ROI ce mois")).toBeInTheDocument();
    expect(screen.getByText("Bénéfice")).toBeInTheDocument();
    expect(screen.getByText("Taux réussite")).toBeInTheDocument();
  });

  it("rend les liens corrects", () => {
    render(<PageJeux />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/jeux/ocr-ticket");
    expect(hrefs).toContain("/jeux/performance");
    expect(hrefs).toContain("/jeux/bankroll");
  });
});
