import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  listerJobs,
  declencherJob,
  declencherJobAvecOptions,
  executerTousLesJobs,
  mettreAJourScheduleJob,
  obtenirLogsJob,
  listerHistoriqueJobs,
  relancerJobDepuisHistorique,
} from "@/bibliotheque/api/admin";

const mockedApi = vi.mocked(clientApi);

describe("API Admin Jobs", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("listerJobs appelle GET /api/v1/admin/jobs", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: [] });

    await listerJobs();

    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/admin/jobs");
  });

  it("declencherJob appelle POST /api/v1/admin/jobs/{id}/run", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { status: "ok", job_id: "job_briefing_matinal_push", message: "ok" } });

    await declencherJob("job_briefing_matinal_push");

    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/admin/jobs/job_briefing_matinal_push/run");
  });

  it("obtenirLogsJob appelle GET /api/v1/admin/jobs/{id}/logs", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: { job_id: "job_nutrition_adultes_weekly", nom: "job", logs: [], total: 0 } });

    await obtenirLogsJob("job_nutrition_adultes_weekly");

    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/admin/jobs/job_nutrition_adultes_weekly/logs");
  });

  it("listerHistoriqueJobs passe les filtres en query params", async () => {
    mockedApi.get.mockResolvedValueOnce({
      data: { items: [], total: 0, page: 1, par_page: 20, pages_totales: 0 },
    });

    await listerHistoriqueJobs({
      page: 1,
      par_page: 20,
      job_id: "job_briefing_matinal_push",
      status: "dry_run",
    });

    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/admin/jobs/history", {
      params: {
        page: 1,
        par_page: 20,
        job_id: "job_briefing_matinal_push",
        status: "dry_run",
      },
    });
  });

  it("declencherJobAvecOptions passe dry_run et force", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { status: "ok", job_id: "job_briefing_matinal_push", message: "ok" } });

    await declencherJobAvecOptions("job_briefing_matinal_push", { dry_run: true, force: true });

    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/admin/jobs/job_briefing_matinal_push/run", null, {
      params: {
        dry_run: true,
        force: true,
      },
    });
  });

  it("executerTousLesJobs appelle POST /run-all", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { mode: "dry_run", total: 0, succes: 0, echecs: 0, items: [] } });

    await executerTousLesJobs({ dry_run: true, force: true });

    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/admin/jobs/run-all", {
      dry_run: true,
      continuer_sur_erreur: true,
      inclure_jobs_inactifs: false,
      force: true,
    });
  });

  it("mettreAJourScheduleJob appelle PUT /schedule", async () => {
    mockedApi.put.mockResolvedValueOnce({ data: { status: "ok", job_id: "job_briefing_matinal_push", schedule: "cron", prochain_run: null } });

    await mettreAJourScheduleJob("job_briefing_matinal_push", "0 8 * * 1");

    expect(mockedApi.put).toHaveBeenCalledWith("/api/v1/admin/jobs/job_briefing_matinal_push/schedule", {
      cron: "0 8 * * 1",
    });
  });

  it("relancerJobDepuisHistorique appelle POST retry avec query params", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { status: "ok", job_id: "job_briefing_matinal_push", message: "ok" } });

    await relancerJobDepuisHistorique(42, { dry_run: true, force: false });

    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/admin/jobs/history/42/retry", null, {
      params: {
        dry_run: true,
        force: false,
      },
    });
  });
});
