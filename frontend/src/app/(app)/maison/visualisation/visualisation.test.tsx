import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import PageVisualisation from "./page";

vi.mock("next/dynamic", () => ({
  default: () => {
    return function Plan3DMock() {
      return <div data-testid="plan3d-mock" />;
    };
  },
}));

vi.mock("@/composants/maison/plan-3d", () => ({
  default: () => <div data-testid="plan3d-module-mock" />,
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock("@/composants/bouton-achat", () => ({
  BoutonAchat: () => <button type="button">Achat</button>,
}));

vi.mock("@/composants/ui/card", () => ({
  Card: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  CardHeader: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  CardTitle: ({ children }: { children: ReactNode }) => <h2>{children}</h2>,
  CardContent: ({ children }: { children: ReactNode }) => <div>{children}</div>,
}));

vi.mock("@/composants/ui/button", () => ({
  Button: ({ children, ...props }: { children: ReactNode }) => <button type="button" {...props}>{children}</button>,
}));

vi.mock("@/composants/ui/badge", () => ({
  Badge: ({ children }: { children: ReactNode }) => <span>{children}</span>,
}));

vi.mock("@/composants/ui/skeleton", () => ({
  Skeleton: () => <div>Chargement</div>,
}));

vi.mock("@/composants/ui/sheet", () => ({
  Sheet: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  SheetContent: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  SheetHeader: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  SheetTitle: ({ children }: { children: ReactNode }) => <h3>{children}</h3>,
}));

vi.mock("@/composants/ui/collapsible", () => ({
  Collapsible: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  CollapsibleContent: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  CollapsibleTrigger: ({ children }: { children: ReactNode }) => <div>{children}</div>,
}));

vi.mock("@tanstack/react-query", () => ({
  useQueryClient: () => ({ invalidateQueries: vi.fn() }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/visualisation",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("etages")) return { data: [0, 1], isLoading: false };
    return { data: [{ id: 1, nom: "Salon", surface: 25, etage: 0 }], isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerPieces: vi.fn(),
  listerEtages: vi.fn(),
  sauvegarderPositions: vi.fn(),
  creerTacheEntretien: vi.fn(),
  obtenirDetailPiece: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe("PageVisualisation", () => {
  it("affiche le titre Plan de la maison", () => {
    render(<PageVisualisation />);
    expect(screen.getByText(/Plan de la maison/)).toBeInTheDocument();
  });

  it("affiche la description", () => {
    render(<PageVisualisation />);
    expect(screen.getByText(/Vue interactive/)).toBeInTheDocument();
  });
});
