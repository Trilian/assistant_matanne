// ═══════════════════════════════════════════════════════════
// Tests — Page Admin/Jobs
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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
  comparerDryRunVsRun: vi.fn().mockResolvedValue({
    generated_at: "2026-04-03T10:00:00",
    fenetre_heures: 168,
    total: 0,
    items: [],
  }),
  declencherJobAvecOptions: vi.fn(),
  executerJobsDuMatin: vi.fn(),
  executerTousLesJobs: vi.fn(),
  listerHistoriqueJobs: vi.fn().mockResolvedValue({
    items: [],
    total: 0,
    page: 1,
    par_page: 20,
    pages_totales: 1,
  }),
  listerJobs: vi.fn(),
  mettreAJourScheduleJob: vi.fn(),
  relancerJobDepuisHistorique: vi.fn(),
  simulerJourneeJobs: vi.fn(),
}));

import {
  declencherJobAvecOptions,
  listerJobs,
} from "@/bibliotheque/api/admin";
import PageAdminJobs from "@/app/(app)/admin/jobs/page";

const mockedDeclencherJobAvecOptions = vi.mocked(declencherJobAvecOptions);
const mockedListerJobs = vi.mocked(listerJobs);

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
  mockedListerJobs.mockResolvedValue(JOBS_MOCK);
  mockedDeclencherJobAvecOptions.mockResolvedValue({
    status: "ok",
    job_id: "job_push_quotidien",
    message: "Job exécuté.",
  });
});

describe("PageAdminJobs — rendu initial", () => {
  it("affiche un loader pendant le chargement", () => {
    mockedListerJobs.mockReturnValue(new Promise(() => {})); // never resolves
    renderWithQuery(React.createElement(PageAdminJobs));
    expect(screen.getByText(/Chargement des jobs/i)).toBeDefined();
  });

  it("affiche la liste des jobs après chargement", async () => {
    mockedListerJobs.mockResolvedValue(JOBS_MOCK);
    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getByText("Push quotidien 20h")).toBeDefined();
    });
    expect(screen.getByText("Rapport mensuel budget")).toBeDefined();
  });

  it("affiche le statut actif en badge", async () => {
    mockedListerJobs.mockResolvedValue(JOBS_MOCK);
    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getAllByText(/actif/i).length).toBeGreaterThan(0);
    });
  });
});

describe("PageAdminJobs — gestion erreur API", () => {
  it("gère gracieusement une erreur API", async () => {
    mockedListerJobs.mockRejectedValue(new Error("API indisponible"));
    renderWithQuery(React.createElement(PageAdminJobs));

    // La page ne doit pas planter
    await waitFor(() => {
      expect(document.body).toBeDefined();
    });
  });
});

describe("PageAdminJobs — exécution dry-run", () => {
  it("propage dry_run=true lors de l'exécution d'un job", async () => {
    mockedListerJobs.mockResolvedValue(JOBS_MOCK);
    mockedDeclencherJobAvecOptions.mockResolvedValue({
      status: "dry_run",
      job_id: "job_push_quotidien",
      message: "Simulation OK",
    });

    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getByText("Push quotidien 20h")).toBeInTheDocument();
    });

    const dryRunCheckbox = screen.getAllByRole("checkbox")[0];
    fireEvent.click(dryRunCheckbox);

    const runButton = screen.getByRole("button", { name: /Exécuter Push quotidien 20h/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(mockedDeclencherJobAvecOptions).toHaveBeenCalledWith(
        "job_push_quotidien",
        { dry_run: true, force: false },
      );
    });
  });

  it("affiche l'état erreur quand l'exécution du job échoue", async () => {
    mockedListerJobs.mockResolvedValue(JOBS_MOCK);
    mockedDeclencherJobAvecOptions.mockRejectedValue(new Error("échec exécution"));

    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getByText("Push quotidien 20h")).toBeInTheDocument();
    });

    const runButton = screen.getByRole("button", { name: /Exécuter Push quotidien 20h/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("Erreur")).toBeInTheDocument();
    });
  });

  it("affiche l'état terminé quand l'exécution réussit", async () => {
    mockedListerJobs.mockResolvedValue(JOBS_MOCK);
    mockedDeclencherJobAvecOptions.mockResolvedValue({
      status: "ok",
      job_id: "job_push_quotidien",
      message: "Job exécuté.",
    });

    renderWithQuery(React.createElement(PageAdminJobs));

    await waitFor(() => {
      expect(screen.getByText("Push quotidien 20h")).toBeInTheDocument();
    });

    const runButton = screen.getByRole("button", { name: /Exécuter Push quotidien 20h/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText("Terminé")).toBeInTheDocument();
    });
  });
});
