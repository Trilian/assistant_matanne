import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageFamille from "@/app/(app)/famille/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (_key: unknown, _fn: unknown) => ({
    data: null,
    isLoading: false,
    error: null,
  }),
}));

describe("PageFamille (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Famille", () => {
    render(<PageFamille />);
    expect(screen.getByText(/Famille/)).toBeInTheDocument();
  });

  it("affiche les 10 sections", () => {
    render(<PageFamille />);
    expect(screen.getByText("Jules")).toBeInTheDocument();
    expect(screen.getByText("Activités")).toBeInTheDocument();
    expect(screen.getByText("Routines")).toBeInTheDocument();
    expect(screen.getByText("Budget")).toBeInTheDocument();
    expect(screen.getByText("Weekend")).toBeInTheDocument();
    expect(screen.getByText("Album")).toBeInTheDocument();
    expect(screen.getByText("Anniversaires")).toBeInTheDocument();
    expect(screen.getByText("Contacts")).toBeInTheDocument();
    expect(screen.getByText("Documents")).toBeInTheDocument();
    expect(screen.getByText("Journal")).toBeInTheDocument();
  });

  it("rend les liens corrects", () => {
    render(<PageFamille />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/famille/jules");
    expect(hrefs).toContain("/famille/budget");
    expect(hrefs).toContain("/famille/routines");
  });
});
