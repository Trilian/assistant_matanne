import { describe, expect, it, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    post: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import { enregistrerActionWidgetDashboard } from "@/bibliotheque/api/tableau-bord";

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
});
