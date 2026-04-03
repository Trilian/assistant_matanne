import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  listerHistoriqueNotifications,
  previsualiserTemplateNotification,
  simulerNotificationAdmin,
} from "@/bibliotheque/api/admin";

const mockedApi = vi.mocked(clientApi);

describe("API Admin Notifications", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("previsualiserTemplateNotification appelle le endpoint preview", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: { status: "ok", canal: "telegram", template_id: "resume_weekend", preview: "demo", contexte_demo: {} } });

    await previsualiserTemplateNotification("telegram", "resume_weekend");

    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/admin/notifications/templates/telegram/resume_weekend/preview");
  });

  it("simulerNotificationAdmin appelle le endpoint simulate", async () => {
    mockedApi.post.mockResolvedValueOnce({ data: { status: "ok", dry_run: true, template: { id: "resume_weekend", label: "Resume", trigger: "CRON" }, payload: {} } });

    await simulerNotificationAdmin({ canal: "telegram", template_id: "resume_weekend", dry_run: true });

    expect(mockedApi.post).toHaveBeenCalledWith("/api/v1/admin/notifications/simulate", {
      canal: "telegram",
      template_id: "resume_weekend",
      dry_run: true,
    });
  });

  it("listerHistoriqueNotifications passe la limite en query params", async () => {
    mockedApi.get.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    await listerHistoriqueNotifications(25);

    expect(mockedApi.get).toHaveBeenCalledWith("/api/v1/admin/notifications/history", {
      params: { limit: 25 },
    });
  });
});