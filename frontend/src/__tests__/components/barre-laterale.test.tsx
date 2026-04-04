import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BarreLaterale } from "@/composants/disposition/barre-laterale";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ prefetch: vi.fn() }),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { role: "admin" } }),
}));

vi.mock("@/magasins/store-ui", () => ({
  utiliserStoreUI: () => ({ sidebarOuverte: true, basculerSidebar: vi.fn() }),
}));

vi.mock("@/crochets/utiliser-badges-modules", () => ({
  utiliserBadgesModules: () => ({
    badges: {
      cuisine: 2,
      famille: 3,
      maison: 1,
      jeux: 4,
    },
    badgePlus: 4,
  }),
}));

describe("BarreLaterale", () => {
  it("affiche les sections principales et leurs badges module", () => {
    render(<BarreLaterale />);

    expect(screen.getByText("Cuisine")).toBeInTheDocument();
    expect(screen.getByText("Famille")).toBeInTheDocument();
    expect(screen.getByText("Maison")).toBeInTheDocument();
    expect(screen.getByText("Jeux")).toBeInTheDocument();

    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });
});
