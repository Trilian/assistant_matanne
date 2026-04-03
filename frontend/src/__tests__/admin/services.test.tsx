import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("@/composants/ui/tabs", () => ({
  Tabs: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  TabsList: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  TabsTrigger: ({ children }: { children: React.ReactNode }) => React.createElement("button", { type: "button" }, children),
  TabsContent: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  executerActionService: vi.fn(),
  exporterConfigAdmin: vi.fn(),
  forcerResync: vi.fn(),
  importerConfigAdmin: vi.fn(),
  lancerSeedDev: vi.fn(),
  lireFeatureFlags: vi.fn(),
  lireRuntimeConfig: vi.fn(),
  listerActionsServices: vi.fn(),
  listerResyncTargets: vi.fn(),
  obtenirDashboardAdmin: vi.fn(),
  obtenirLiveSnapshotAdmin: vi.fn(),
  obtenirSanteServices: vi.fn(),
  obtenirStatutBridgesPhase5: vi.fn(),
  obtenirStatsCache: vi.fn(),
  purgerCache: vi.fn(),
  sauvegarderFeatureFlags: vi.fn(),
  sauvegarderRuntimeConfig: vi.fn(),
  simulerFluxAdmin: vi.fn(),
  viderCache: vi.fn(),
}));

import {
  exporterConfigAdmin,
  importerConfigAdmin,
  lireFeatureFlags,
  lireRuntimeConfig,
  listerActionsServices,
  listerResyncTargets,
  obtenirDashboardAdmin,
  obtenirLiveSnapshotAdmin,
  obtenirSanteServices,
  obtenirStatutBridgesPhase5,
  obtenirStatsCache,
  simulerFluxAdmin,
} from "@/bibliotheque/api/admin";
import PageAdminServices from "@/app/(app)/admin/services/page";

const mockedExporterConfigAdmin = vi.mocked(exporterConfigAdmin);
const mockedImporterConfigAdmin = vi.mocked(importerConfigAdmin);
const mockedLireFeatureFlags = vi.mocked(lireFeatureFlags);
const mockedLireRuntimeConfig = vi.mocked(lireRuntimeConfig);
const mockedListerActionsServices = vi.mocked(listerActionsServices);
const mockedListerResyncTargets = vi.mocked(listerResyncTargets);
const mockedObtenirDashboardAdmin = vi.mocked(obtenirDashboardAdmin);
const mockedObtenirLiveSnapshotAdmin = vi.mocked(obtenirLiveSnapshotAdmin);
const mockedObtenirSanteServices = vi.mocked(obtenirSanteServices);
const mockedObtenirStatutBridgesPhase5 = vi.mocked(obtenirStatutBridgesPhase5);
const mockedObtenirStatsCache = vi.mocked(obtenirStatsCache);
const mockedSimulerFluxAdmin = vi.mocked(simulerFluxAdmin);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

describe("PageAdminServices", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(HTMLElement.prototype, "scrollIntoView", {
      configurable: true,
      writable: true,
      value: vi.fn(),
    });

    mockedObtenirSanteServices.mockResolvedValue({
      global_status: "healthy",
      total_services: 3,
      instantiated: 2,
      healthy: 2,
      erreurs: [],
      services: {
        cache: { status: "healthy", note: "OK" },
      },
    });
    mockedObtenirStatsCache.mockResolvedValue({ l1_hits: 4, l3_hits: 2, misses: 1, writes: 3 });
    mockedObtenirDashboardAdmin.mockResolvedValue({
      generated_at: "2026-03-30T12:00:00",
      jobs: { total: 5, actifs: 4, inactifs: 1 },
      services: {
        global_status: "healthy",
        total_services: 3,
        instantiated: 2,
        healthy: 2,
        erreurs: [],
        services: {},
      },
      metriques_services: {},
      cache: {},
      security: { events_24h: 7 },
      feature_flags: { "admin.mode_test": false },
    });
    mockedListerActionsServices.mockResolvedValue({
      items: [
        {
          id: "automations.executer",
          service: "moteur_automations",
          description: "Exécuter le moteur d'automations actif.",
          dry_run: true,
        },
      ],
      total: 1,
      enabled: true,
    });
    mockedLireFeatureFlags.mockResolvedValue({
      flags: { "admin.mode_test": false, "admin.service_actions_enabled": true },
      total: 2,
    });
    mockedLireRuntimeConfig.mockResolvedValue({
      values: { "dashboard.refresh_seconds": 300 },
      readonly: { env: "development" },
    });
    mockedListerResyncTargets.mockResolvedValue({
      items: [{ id: "garmin", job_id: "garmin_sync_matinal", description: "Forcer la synchronisation Garmin." }],
      total: 1,
      enabled: true,
    });
    mockedObtenirLiveSnapshotAdmin.mockResolvedValue({
      generated_at: "2026-03-30T12:00:00",
      api: {
        uptime_seconds: 120,
        requests_total: 42,
        top_endpoints: [{ endpoint: "GET:/api/v1/admin/live-snapshot", count: 12 }],
        latency: { avg_ms: 15.2, p95_ms: 24.1, tracked_endpoints: 3 },
        rate_limiting: {},
        ai: {},
      },
      cache: {},
      jobs: { last_24h: { success: 5, dry_run: 1 } },
      security: { events_1h: 2 },
    });
    mockedObtenirStatutBridgesPhase5.mockResolvedValue({
      phase: "bridges_inter_modules",
      generated_at: "2026-03-30T12:00:00",
      execution_ms: 12.4,
      statut_global: "operationnel",
      resume: {
        total_actions: 17,
        operationnelles: 17,
        indisponibles: 0,
        taux_operationnel_pct: 100,
        mode_verification: "presence_only",
      },
      items: [
        {
          id: "P5-01",
          bridge: "inter_module_inventaire_planning.py",
          intitule: "Stock -> Planning recettes",
          verification: "presence",
          statut: "operationnel",
          latence_ms: 2.5,
          details: "Factory et méthode disponibles.",
        },
      ],
    });
    mockedExporterConfigAdmin.mockResolvedValue({
      exported_at: "2026-03-30T12:00:00",
      feature_flags: { "admin.mode_test": false },
      runtime_config: { "dashboard.refresh_seconds": 300 },
    });
    mockedImporterConfigAdmin.mockResolvedValue({
      status: "ok",
      feature_flags: { "admin.mode_test": true },
      runtime_config: { "dashboard.refresh_seconds": 60 },
    });
    mockedSimulerFluxAdmin.mockResolvedValue({
      scenario: "peremption_j2",
      user_id: "admin",
      dry_run: true,
      actions: [{ type: "notification.preparee", canaux: ["push", "ntfy"] }],
      payload: {},
    });

    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:test"),
      revokeObjectURL: vi.fn(),
    });

    const originalCreateElement = Document.prototype.createElement;
    vi.spyOn(document, "createElement").mockImplementation(((tagName: string) => {
      if (tagName === "a") {
        return { click: vi.fn(), href: "", download: "" } as unknown as HTMLElement;
      }
      return originalCreateElement.call(document, tagName);
    }) as typeof document.createElement);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("affiche les métriques live et le top endpoint", async () => {
    renderWithQuery(React.createElement(PageAdminServices));

    await waitFor(() => {
      expect(screen.getByText("42")).toBeInTheDocument();
    });

    expect(screen.getByText(/latence moyenne/i)).toBeInTheDocument();
    expect(screen.getByText(/GET:\/api\/v1\/admin\/live-snapshot/i)).toBeInTheDocument();
  });

  it("importe la configuration admin depuis le JSON collé", async () => {
    renderWithQuery(React.createElement(PageAdminServices));

    await screen.findByRole("button", { name: /importer la configuration/i });
    const importTextarea = await screen.findByPlaceholderText(/collez ici un export json admin/i);
    fireEvent.change(importTextarea, {
      target: {
        value: JSON.stringify({
          feature_flags: { "admin.mode_test": true },
          runtime_config: { "dashboard.refresh_seconds": 60 },
        }),
      },
    });

    fireEvent.click(screen.getByRole("button", { name: /importer la configuration/i }));

    await waitFor(() => {
      expect(mockedImporterConfigAdmin).toHaveBeenCalledWith({
        feature_flags: { "admin.mode_test": true },
        runtime_config: { "dashboard.refresh_seconds": 60 },
        merge: true,
      });
    });
  });

  it("lance une simulation de flux depuis l'onglet simulateur", async () => {
    renderWithQuery(React.createElement(PageAdminServices));

    await screen.findByLabelText(/scénario de simulation/i);
    fireEvent.click(await screen.findByRole("button", { name: /lancer la simulation/i }));

    await waitFor(() => {
      expect(mockedSimulerFluxAdmin).toHaveBeenCalledWith({
        scenario: "peremption_j2",
        message: undefined,
        dry_run: true,
      });
    });

    expect(screen.getByText(/notification.preparee/i)).toBeInTheDocument();
  });
});