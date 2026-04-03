import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import PageVisualisation from "./page";

const mockPush = vi.fn();
const mockInvalidateQueries = vi.fn();
const mockMutate = vi.fn();

const piecesMock = [
  {
    id: 1,
    nom: "Salon",
    etage: 0,
    surface_m2: 25,
    position_x: 120,
    position_y: 90,
    largeur: 180,
    hauteur: 130,
    couleur: "#34d399",
    objets: [{ id: 10, nom: "TV", type: "electronique", statut: "hors_service" }],
  },
];

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
  useQueryClient: () => ({ invalidateQueries: mockInvalidateQueries }),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, back: vi.fn() }),
  usePathname: () => "/maison/visualisation",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockImplementation((key: string[]) => {
    if (key.includes("etages")) {
      return { data: [0, 1], isLoading: false };
    }

    if (key.includes("entretien")) {
      return {
        data: [{ id: 1, piece: "Salon", fait: false, prochaine_fois: "2024-01-01" }],
        isLoading: false,
      };
    }

    if (key.includes("detail")) {
      return {
        data: {
          objets: [{ id: 10, nom: "TV", type: "electronique", statut: "hors_service" }],
        },
        isLoading: false,
      };
    }

    return { data: piecesMock, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: mockMutate, isPending: false }),
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
    expect(screen.getByRole("button", { name: /^Salon$/i })).toBeInTheDocument();
  });

  it("active le mode édition", async () => {
    const user = userEvent.setup();
    render(<PageVisualisation />);

    await user.click(screen.getByRole("button", { name: /Modifier positions/i }));

    expect(screen.getByRole("button", { name: /Édition active/i })).toBeInTheDocument();
  });

  it("ouvre les détails d'une pièce et permet la navigation d'action", async () => {
    const user = userEvent.setup();
    render(<PageVisualisation />);

    await user.click(screen.getByRole("button", { name: /^Salon$/i }));

    expect(screen.getByText(/Ménage rapide/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Entretien rapide/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Entretien rapide/i }));
    expect(mockPush).toHaveBeenCalledWith("/maison/travaux?tab=entretien");
  });
});
