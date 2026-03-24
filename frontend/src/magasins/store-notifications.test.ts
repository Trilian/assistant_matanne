import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { utiliserStoreNotifications } from "./store-notifications";

describe("store-notifications", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    utiliserStoreNotifications.getState().vider();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("ajoute une notification", () => {
    const { ajouter } = utiliserStoreNotifications.getState();
    ajouter({ type: "succes", message: "Opération réussie" });

    const { notifications } = utiliserStoreNotifications.getState();
    expect(notifications).toHaveLength(1);
    expect(notifications[0].message).toBe("Opération réussie");
    expect(notifications[0].type).toBe("succes");
    expect(notifications[0].id).toBeDefined();
  });

  it("retire une notification par id", () => {
    const { ajouter } = utiliserStoreNotifications.getState();
    ajouter({ type: "info", message: "Test" });

    const id = utiliserStoreNotifications.getState().notifications[0].id;
    utiliserStoreNotifications.getState().retirer(id);

    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(0);
  });

  it("vide toutes les notifications", () => {
    const { ajouter } = utiliserStoreNotifications.getState();
    ajouter({ type: "succes", message: "A" });
    ajouter({ type: "erreur", message: "B" });
    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(2);

    utiliserStoreNotifications.getState().vider();
    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(0);
  });

  it("auto-retire après 5 secondes", () => {
    const { ajouter } = utiliserStoreNotifications.getState();
    ajouter({ type: "attention", message: "Temporaire" });
    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(1);

    vi.advanceTimersByTime(5000);
    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(0);
  });

  it("gère plusieurs notifications", () => {
    const { ajouter } = utiliserStoreNotifications.getState();
    ajouter({ type: "succes", message: "Premier" });
    ajouter({ type: "erreur", message: "Deuxième", titre: "Erreur" });

    const notifs = utiliserStoreNotifications.getState().notifications;
    expect(notifs).toHaveLength(2);
    expect(notifs[1].titre).toBe("Erreur");
  });
});
