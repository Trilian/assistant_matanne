import { describe, expect, it, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  enregistrerActionWidgetDashboard,
  obtenirHistoriqueActionsWidgetsDashboard,
} from "@/bibliotheque/api/tableau-bord";

describe("API dashboard widgets/action", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("poste l'action widget avec donnees", async () => {
    vi.mocked(clientApi.post).mockResolvedValueOnce({
      data: {
        widget_id: "checklist_jour",
        action: "valider_tache",
        statut: "ok",
      },
    } as never);

    const result = await enregistrerActionWidgetDashboard({
      widget_id: "checklist_jour",
      action: "valider_tache",
      donnees: { id_source: 42, fait: true },
    });

    expect(clientApi.post).toHaveBeenCalledWith("/dashboard/widgets/action", {
      widget_id: "checklist_jour",
      action: "valider_tache",
      donnees: { id_source: 42, fait: true },
    });
    expect(result.statut).toBe("ok");
  });

  it("poste l'action widget avec donnees vides par défaut", async () => {
    vi.mocked(clientApi.post).mockResolvedValueOnce({
      data: {
        widget_id: "metriques",
        action: "masquer",
        statut: "ok",
      },
    } as never);

    await enregistrerActionWidgetDashboard({
      widget_id: "metriques",
      action: "masquer",
    });

    expect(clientApi.post).toHaveBeenCalledWith("/dashboard/widgets/action", {
      widget_id: "metriques",
      action: "masquer",
      donnees: {},
    });
  });

  it("lit l'historique des actions widgets", async () => {
    vi.mocked(clientApi.get).mockResolvedValueOnce({
      data: {
        items: [
          {
            event_id: "evt_1",
            type: "dashboard.widget.action_rapide",
            source: "dashboard",
            timestamp: "2026-04-02T21:00:00",
            widget_id: "checklist_jour",
            action: "valider_tache",
            donnees: { id_source: 42 },
          },
        ],
        total: 1,
      },
    } as never);

    const result = await obtenirHistoriqueActionsWidgetsDashboard(8);

    expect(clientApi.get).toHaveBeenCalledWith("/dashboard/widgets/actions", {
      params: { limite: 8 },
    });
    expect(result.total).toBe(1);
    expect(result.items[0]?.action).toBe("valider_tache");
  });
});
