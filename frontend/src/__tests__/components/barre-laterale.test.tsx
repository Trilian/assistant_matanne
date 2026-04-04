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

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: { rappels: [], total: 0 } }),
}));

describe("BarreLaterale", () => {
  it("affiche les sections principales", () => {
    render(<BarreLaterale />);

    expect(screen.getByText("Cuisine")).toBeInTheDocument();
    expect(screen.getByText("Famille")).toBeInTheDocument();
    expect(screen.getByText("Maison")).toBeInTheDocument();
    expect(screen.getByText("Jeux")).toBeInTheDocument();
  });
});
