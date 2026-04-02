import { describe, it, expect, vi, beforeEach } from "vitest";
import { render } from "@testing-library/react";
import PagePlanning from "./page";

const { mockRedirect } = vi.hoisted(() => ({
  mockRedirect: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/planning",
  redirect: mockRedirect,
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("PagePlanning", () => {
  beforeEach(() => vi.clearAllMocks());

  it("redirige vers /cuisine/planning", () => {
    PagePlanning();
    expect(mockRedirect).toHaveBeenCalledWith("/cuisine/planning");
  });
});
