import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageOutils from "@/app/(app)/outils/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/outils",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("PageOutils (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Outils", () => {
    render(<PageOutils />);
    expect(screen.getByText(/Outils/)).toBeInTheDocument();
  });

  it("affiche les 5 sections", () => {
    render(<PageOutils />);
    expect(screen.getByText("Chat IA")).toBeInTheDocument();
    expect(screen.getByText("Notes")).toBeInTheDocument();
    expect(screen.getByText("Météo")).toBeInTheDocument();
    expect(screen.getByText("Minuteur")).toBeInTheDocument();
    expect(screen.getByText("Convertisseur")).toBeInTheDocument();
  });

  it("rend les liens corrects", () => {
    render(<PageOutils />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/outils/chat-ia");
    expect(hrefs).toContain("/outils/notes");
    expect(hrefs).toContain("/outils/meteo");
    expect(hrefs).toContain("/outils/minuteur");
    expect(hrefs).toContain("/outils/convertisseur");
  });
});
