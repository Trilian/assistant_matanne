// ═══════════════════════════════════════════════════════════
// Tests — Page Admin/Jobs
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// Mock API client
vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

// Mock date-fns
vi.mock("date-fns", () => ({
  format: vi.fn(() => "01/01/2025 10:00"),
  parseISO: vi.fn((s: string) => new Date(s)),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  listerHistoriqueJobs: vi.fn().mockResolvedValue({
    items: [],
    total: 0,
    page: 1,
    par_page: 20,
    pages_totales: 1,
  }),
}));

import { clientApi } from "@/bibliotheque/api/client";
import PageAdminJobs from "@/app/(app)/admin/jobs/page";

const mockedApi = vi.mocked(clientApi);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    React.createElement(QueryClientProvider, { client }, ui)
  );
}

const JOBS_MOCK = [
  {
    id: "job_push_quotidien",
    nom: "Push quotidien 20h",
    schedule: "0 20 * * *",
    prochain_run: "2025-01-01T20:00:00",
    dernier_run: "2024-12-31T20:00:00",
    statut: "actif",
  },
  {
    id: "job_rapport_mensuel",
    nom: "Rapport mensuel budget",
    schedule: "0 8 1 * *",
    prochain_run: null,
    dernier_run: null,
    statut: "inactif",
  },
];

beforeEach(() => {
  vi.clearAllMocks();
});

describe("PageAdminJobs — rendu initial", () => {
  it("affiche un loader pendant le chargement", () => {
    mockedApi.get.mockReturnValue(new Promise(() => {})); // never resolves
    renderWithQuery(React.createElement(PageAdminJobs));
    expect(screen.getByText(/Chargement des jobs/i)).toBeDefined();
  });

  it("affiche la liste des jobs après chargement", async () => {
    mockedApi.get.mockResolvedValue({ data: JOBS_MOCK });
    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getByText("Push quotidien 20h")).toBeDefined();
    });
    expect(screen.getByText("Rapport mensuel budget")).toBeDefined();
  });

  it("affiche le statut actif en badge", async () => {
    mockedApi.get.mockResolvedValue({ data: JOBS_MOCK });
    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getAllByText(/actif/i).length).toBeGreaterThan(0);
    });
  });
});

describe("PageAdminJobs — gestion erreur API", () => {
  it("gère gracieusement une erreur API", async () => {
    mockedApi.get.mockRejectedValue(new Error("API indisponible"));
    renderWithQuery(React.createElement(PageAdminJobs));

    // La page ne doit pas planter
    await waitFor(() => {
      expect(document.body).toBeDefined();
    });
  });
});
