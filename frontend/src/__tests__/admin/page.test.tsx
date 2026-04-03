import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("next/link", () => ({
  default: ({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) => (
    React.createElement("a", { href, className }, children)
  ),
}));

vi.mock("recharts", () => ({
  BarChart: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  Bar: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  XAxis: () => React.createElement("div"),
  YAxis: () => React.createElement("div"),
  Tooltip: () => React.createElement("div"),
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  Cell: () => React.createElement("div"),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  obtenirStatutBridges: vi.fn(),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import { obtenirStatutBridges } from "@/bibliotheque/api/admin";
import { clientApi } from "@/bibliotheque/api/client";
import PageAdmin from "@/app/(app)/admin/page";

const mockedObtenirStatutBridges = vi.mocked(obtenirStatutBridges);
const mockedClientApiGet = vi.mocked(clientApi.get);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

describe("PageAdmin", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockedClientApiGet.mockImplementation(async (url: string) => {
      if (url.includes("/admin/audit-logs")) {
        return {
          data: {
            items: [],
            total: 0,
            page: 1,
            par_page: 25,
            pages_totales: 1,
          },
        };
      }
      if (url.includes("/admin/audit-stats")) {
        return {
          data: {
            total_entrees: 3,
            par_action: { "admin.login": 2, "admin.refresh": 1 },
            par_entite: { admin: 3 },
            par_source: { admin: 3 },
            souscrit_bus: true,
          },
        };
      }
      if (url.includes("/admin/users")) {
        return { data: [] };
      }
      if (url.includes("/admin/cache/stats")) {
        return { data: { l1_hits: 1, misses: 0 } };
      }
      if (url.includes("/admin/security-logs")) {
        return { data: { items: [] } };
      }
      if (url.includes("/admin/audit-export")) {
        return { data: new Blob(["id"]), status: 200 };
      }
      return { data: {} };
    });

    mockedObtenirStatutBridges.mockResolvedValue({
      phase: "bridges_inter_modules",
      generated_at: "2026-04-01T09:00:00",
      execution_ms: 11.2,
      statut_global: "operationnel",
      resume: {
        total_actions: 17,
        operationnelles: 16,
        indisponibles: 1,
        taux_operationnel_pct: 94.12,
        mode_verification: "presence_only",
      },
      items: [],
    });
  });

  it("affiche la synthese Bridges inter-modules et le lien vers le detail", async () => {
    renderWithQuery(React.createElement(PageAdmin));

    await waitFor(() => {
      expect(screen.getByText(/Bridges inter-modules/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/presence_only/i)).toBeInTheDocument();
    expect(screen.getByText(/17 action\(s\)/i)).toBeInTheDocument();
    expect(screen.getByText(/16 OK/i)).toBeInTheDocument();
    expect(screen.getByText(/1 KO/i)).toBeInTheDocument();

    const lien = screen.getByRole("link", { name: /Voir le détail/i });
    expect(lien).toHaveAttribute("href", "/admin/services");
  });
});
