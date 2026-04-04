import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { NavMobile } from "@/composants/disposition/nav-mobile";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ prefetch: vi.fn(), push: vi.fn() }),
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

describe("NavMobile", () => {
  it("affiche des indicateurs de badge sur les modules principaux et le drawer plus", async () => {
    const user = userEvent.setup();
    render(<NavMobile />);

    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getAllByText("4").length).toBeGreaterThanOrEqual(1);

    await user.click(screen.getByRole("button", { name: /plus de sections/i }));
    expect(screen.getByText("Jeux")).toBeInTheDocument();
  });
});
