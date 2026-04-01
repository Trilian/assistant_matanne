import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageFamille from "@/app/(app)/famille/page";

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({ invalidateQueries: vi.fn() }),
  useMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

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
  utiliserRequete: (queryKey: unknown) => {
    const key = Array.isArray(queryKey) ? queryKey.join(":") : "";

    if (key.includes("contexte")) {
      return {
        data: {
          anniversaires_proches: [],
          documents_expirants: [],
          jours_speciaux: [],
        },
        isLoading: false,
        error: null,
      };
    }

    if (key.includes("rappels")) {
      return {
        data: { rappels: [], total: 0 },
        isLoading: false,
        error: null,
      };
    }

    if (key.includes("achats")) {
      return {
        data: [],
        isLoading: false,
        error: null,
      };
    }

    if (key.includes("budget")) {
      return {
        data: {
          total_courant: 0,
          variation_pct: 0,
        },
        isLoading: false,
        error: null,
      };
    }

    return {
      data: null,
      isLoading: false,
      error: null,
    };
  },
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

describe("PageFamille (Hub)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Famille", () => {
    render(<PageFamille />);
    expect(screen.getByRole("heading", { name: /Famille/ })).toBeInTheDocument();
  });

  it("affiche les modules de navigation", () => {
    render(<PageFamille />);
    expect(screen.getAllByText("Jules").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Budget").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Routines").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Achats").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Contacts").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Documents").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Calendriers").length).toBeGreaterThan(0);
  });

  it("rend les liens corrects", () => {
    render(<PageFamille />);
    const links = screen.getAllByRole("link");
    const hrefs = links.map((l) => l.getAttribute("href"));
    expect(hrefs).toContain("/famille/jules");
    expect(hrefs).toContain("/famille/budget");
    expect(hrefs).toContain("/famille/routines");
    expect(hrefs).toContain("/famille/achats");
  });
});
