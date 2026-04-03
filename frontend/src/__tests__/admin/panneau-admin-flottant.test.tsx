import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, beforeEach, expect, vi } from "vitest";

vi.mock("@/crochets/utiliser-auth", () => ({
  utiliserAuth: vi.fn(),
}));

vi.mock("@/bibliotheque/api/admin", () => ({
  basculerModeMaintenance: vi.fn(),
  listerJobs: vi.fn(async () => []),
  lireFeatureFlags: vi.fn(),
  lireModeMaintenance: vi.fn(async () => ({ maintenance_mode: false })),
  lireRuntimeConfig: vi.fn(),
  obtenirLiveSnapshotAdmin: vi.fn(async () => ({
    api: { requests_total: 0, ai: {} },
  })),
}));

import { utiliserAuth } from "@/crochets/utiliser-auth";
import { lireFeatureFlags, lireRuntimeConfig } from "@/bibliotheque/api/admin";
import { PanneauAdminFlottant } from "@/composants/disposition/panneau-admin-flottant";

const mockedUtiliserAuth = vi.mocked(utiliserAuth);
const mockedLireFeatureFlags = vi.mocked(lireFeatureFlags);
const mockedLireRuntimeConfig = vi.mocked(lireRuntimeConfig);

describe("PanneauAdminFlottant", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUtiliserAuth.mockReturnValue({
      utilisateur: { role: "admin" },
    } as ReturnType<typeof utiliserAuth>);
  });

  it("reste masque en production sans admin.mode_test", async () => {
    mockedLireFeatureFlags.mockResolvedValue({
      flags: { "admin.mode_test": false },
      total: 1,
    });
    mockedLireRuntimeConfig.mockResolvedValue({
      values: {},
      readonly: { env: "production" },
    });

    render(<PanneauAdminFlottant />);

    await waitFor(() => {
      expect(mockedLireRuntimeConfig).toHaveBeenCalled();
    });
    expect(screen.queryByLabelText(/ouvrir le panneau admin flottant/i)).not.toBeInTheDocument();
  });

  it("s'affiche en environnement development", async () => {
    mockedLireFeatureFlags.mockResolvedValue({
      flags: { "admin.mode_test": false },
      total: 1,
    });
    mockedLireRuntimeConfig.mockResolvedValue({
      values: {},
      readonly: { env: "development" },
    });

    render(<PanneauAdminFlottant />);

    await waitFor(() => {
      expect(screen.getByLabelText(/ouvrir le panneau admin flottant/i)).toBeInTheDocument();
    });
  });
});