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
    data: { paris_actifs: 5, gain_total: 120.5, taux_reussite: 68 },
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
    expect(screen.getByText("Paris sportifs")).toBeInTheDocument();
    expect(screen.getByText("Loto")).toBeInTheDocument();
    expect(screen.getByText("Euromillions")).toBeInTheDocument();
  });

  it("affiche les stats paris", () => {
    render(<PageJeux />);
    expect(screen.getByText("Paris actifs")).toBeInTheDocument();
    expect(screen.getByText("Gains totaux")).toBeInTheDocument();
    expect(screen.getByText("Taux de réussite")).toBeInTheDocument();
  });

  it("rend les liens corrects", () => {
    render(<PageJeux />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/jeux/paris");
    expect(hrefs).toContain("/jeux/loto");
    expect(hrefs).toContain("/jeux/euromillions");
  });
});
