import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

vi.mock("recharts", () => ({
  BarChart: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  Bar: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  XAxis: () => React.createElement("div"),
  YAxis: () => React.createElement("div"),
  Tooltip: () => React.createElement("div"),
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => React.createElement("div", null, children),
  Cell: () => React.createElement("div"),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

vi.mock("date-fns", () => ({
  format: vi.fn(() => "02/04 19:30"),
  parseISO: vi.fn((s: string) => new Date(s)),
  differenceInMinutes: vi.fn(() => 90),
}));

import { clientApi } from "@/bibliotheque/api/client";
import PageAdminScheduler from "@/app/(app)/admin/scheduler/page";

const mockedApi = vi.mocked(clientApi);

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(React.createElement(QueryClientProvider, { client }, ui));
}

const JOBS = [
  {
    id: "job_briefing_matinal_push",
    nom: "S15.7 Briefing matinal IA (07h00)",
    schedule: "cron[hour='7', minute='0']",
    prochain_run: "2026-04-03T07:00:00",
    dernier_run: null,
    statut: "actif",
  },
  {
    id: "job_energie_peak_detection",
    nom: "S15.5 Détection pics énergie (19h00)",
    schedule: "cron[hour='19', minute='0']",
    prochain_run: "2026-04-02T19:00:00",
    dernier_run: null,
    statut: "actif",
  },
] as const;

describe("PageAdminScheduler", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedApi.get.mockResolvedValue({ data: JOBS });
    mockedApi.post.mockResolvedValue({ data: { status: "ok" } });
  });

  it("affiche les jobs Sprint 15 et la catégorie calculée", async () => {
    renderWithQuery(React.createElement(PageAdminScheduler));

    await waitFor(() => {
      expect(screen.getByText("job_briefing_matinal_push")).toBeInTheDocument();
    });

    expect(screen.getByText("job_energie_peak_detection")).toBeInTheDocument();
    expect(screen.getAllByText("Notifications").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Maison").length).toBeGreaterThan(0);
  });

  it("déclenche un job via le bouton play", async () => {
    renderWithQuery(React.createElement(PageAdminScheduler));

    await waitFor(() => {
      expect(screen.getByText("job_briefing_matinal_push")).toBeInTheDocument();
    });

    const rowLabel = screen.getByText("job_briefing_matinal_push");
    const row = rowLabel.closest("tr");
    expect(row).toBeTruthy();

    const rowButtons = row?.querySelectorAll("button") ?? [];
    const runButton = rowButtons[rowButtons.length - 1] as HTMLElement;
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(mockedApi.post).toHaveBeenCalled();
    });
    expect(mockedApi.post.mock.calls[0]?.[0]).toMatch(/\/api\/v1\/admin\/jobs\/.+\/run/);
  });
});
