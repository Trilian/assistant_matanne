import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageDashboard from "@/app/(app)/page";

// ─── Mocks ────────────────────────────────────────────────

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn(), refresh: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/",
  redirect: vi.fn(),
}));

vi.mock("next/dynamic", () => ({
  __esModule: true,
  default: () => {
    const DummyComponent = () => <div data-testid="dynamic-component" />;
    DummyComponent.displayName = "DynamicComponent";
    return DummyComponent;
  },
}));

vi.mock("next/link", () => ({
  __esModule: true,
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn(), promise: vi.fn() },
}));

const mockTableauBord = {
  repas_du_jour: { dejeuner: "Salade niçoise", diner: "Gratin de courgettes" },
  alertes: [{ type: "peremption", message: "Yaourt expire demain", priorite: "haute" }],
  taches: [{ id: 1, nom: "Arroser plantes", fait: false }],
  score: 85,
};

vi.mock("@/bibliotheque/api/tableau-bord", () => ({
  obtenirBilanMensuel: vi.fn().mockResolvedValue({ depenses: 1200, revenus: 3000 }),
  obtenirAlertesContextuelles: vi.fn().mockResolvedValue({ alertes: [] }),
  obtenirConfigDashboard: vi.fn().mockResolvedValue({ widgets: [] }),
  obtenirHistoriqueActionsWidgetsDashboard: vi.fn().mockResolvedValue({ actions: [] }),
  enregistrerActionWidgetDashboard: vi.fn().mockResolvedValue({ ok: true }),
  obtenirPointsFamille: vi.fn().mockResolvedValue({ points: 50 }),
  obtenirScoreEcologique: vi.fn().mockResolvedValue({ score: 72 }),
  obtenirScoreBienEtre: vi.fn().mockResolvedValue({ score: 80 }),
  obtenirScoreFoyer: vi.fn().mockResolvedValue({ score: 85 }),
  obtenirTableauBord: vi.fn().mockResolvedValue(mockTableauBord),
  sauvegarderConfigDashboard: vi.fn().mockResolvedValue({ ok: true }),
}));

vi.mock("@/bibliotheque/api/famille", () => ({
  obtenirAnomaliesBudget: vi.fn().mockResolvedValue({ anomalies: [] }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  modifierTacheEntretien: vi.fn().mockResolvedValue({ ok: true }),
  obtenirTachesJourMaison: vi.fn().mockResolvedValue([]),
  statsDepensesMaison: vi.fn().mockResolvedValue({ total: 0 }),
}));

vi.mock("@/bibliotheque/api/push", () => ({
  evaluerRappels: vi.fn().mockResolvedValue([]),
}));

vi.mock("@/bibliotheque/api/planning", () => ({
  genererPlanningSemaine: vi.fn().mockResolvedValue({}),
}));

vi.mock("@/bibliotheque/api/courses", () => ({
  genererCoursesDepuisPlanning: vi.fn().mockResolvedValue({ articles: [] }),
}));

vi.mock("@/bibliotheque/api/avance", () => ({
  obtenirScoreFamilleHebdo: vi.fn().mockResolvedValue({ score: 90 }),
  obtenirInsightsQuotidiens: vi.fn().mockResolvedValue({ insights: [] }),
}));

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: () => ({ utilisateur: { id: 1, nom: "Test", role: "admin" }, connecte: true }),
}));

vi.mock("@/crochets/utiliser-stockage-local", () => ({
  utiliserStockageLocal: vi.fn().mockReturnValue([null, vi.fn()]),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: { get: vi.fn().mockResolvedValue({ data: {} }), post: vi.fn().mockResolvedValue({ data: {} }) },
}));

vi.mock("@/composants/swipeable-item", () => ({
  SwipeableItem: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock("@/composants/dashboard/grille-dashboard-dnd", () => ({
  GrilleDashboardDnd: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  WidgetSortable: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock("@/composants/dashboard/compteur-anime", () => ({
  CompteurAnime: ({ valeur }: { valeur: number }) => <span>{valeur}</span>,
}));

const mockUtiliserRequete = vi.fn().mockReturnValue({ data: undefined, isLoading: false, error: null });
const mockUtiliserMutation = vi.fn().mockReturnValue({ mutate: vi.fn(), mutateAsync: vi.fn(), isPending: false });

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: (...args: unknown[]) => mockUtiliserRequete(...args),
  utiliserMutation: (...args: unknown[]) => mockUtiliserMutation(...args),
  utiliserInvalidation: vi.fn().mockReturnValue(vi.fn()),
}));

// ─── Helpers ──────────────────────────────────────────────

function renderDashboard() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <PageDashboard />
    </QueryClientProvider>
  );
}

// ─── Tests ────────────────────────────────────────────────

describe("PageDashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUtiliserRequete.mockReturnValue({ data: undefined, isLoading: false, error: null });
  });

  it("rend sans crash", () => {
    renderDashboard();
    expect(document.body).toBeTruthy();
  });

  it("affiche le contenu principal", async () => {
    renderDashboard();
    await waitFor(() => {
      // Le dashboard doit rendre un contenu visible
      expect(document.body.textContent).toBeTruthy();
    });
  });

  it("gère l'état de chargement sans crash", () => {
    mockUtiliserRequete.mockReturnValue({ data: undefined, isLoading: true, error: null });
    renderDashboard();
    expect(document.body).toBeTruthy();
  });

  it("gère une erreur API sans crash", () => {
    mockUtiliserRequete.mockReturnValue({ data: undefined, isLoading: false, error: new Error("Network error") });
    renderDashboard();
    expect(document.body).toBeTruthy();
  });

  it("contient des liens de navigation vers les modules", async () => {
    renderDashboard();
    await waitFor(() => {
      const links = document.querySelectorAll("a[href]");
      expect(links.length).toBeGreaterThan(0);
    });
  });
});
