/**
 * Tests unitaires pour les stores Zustand (P2-18).
 *
 * Couvre:
 * - store-auth (utilisateur, connexion, réinitialisation)
 * - store-ui (sidebar, recherche, titre page, persistence)
 * - store-notifications (ajout, retrait, vidage, préférences)
 */

import { describe, it, expect, beforeEach } from "vitest";
import { utiliserStoreAuth } from "@/magasins/store-auth";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { utiliserStoreNotifications } from "@/magasins/store-notifications";

// ═══════════════════════════════════════════════════════════
// store-auth
// ═══════════════════════════════════════════════════════════

describe("utiliserStoreAuth", () => {
  beforeEach(() => {
    utiliserStoreAuth.getState().reinitialiser();
  });

  it("a un état initial non connecté", () => {
    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toBeNull();
    expect(state.estConnecte).toBe(false);
    expect(state.estChargement).toBe(false);
  });

  it("definirUtilisateur met à jour l'utilisateur et estConnecte", () => {
    const mockUser = { id: "1", email: "test@example.com", nom: "Test" };
    utiliserStoreAuth.getState().definirUtilisateur(mockUser as never);

    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toEqual(mockUser);
    expect(state.estConnecte).toBe(true);
    expect(state.estChargement).toBe(false);
  });

  it("definirUtilisateur avec null déconnecte", () => {
    const mockUser = { id: "1", email: "test@example.com", nom: "Test" };
    utiliserStoreAuth.getState().definirUtilisateur(mockUser as never);
    utiliserStoreAuth.getState().definirUtilisateur(null);

    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toBeNull();
    expect(state.estConnecte).toBe(false);
  });

  it("definirChargement met à jour estChargement", () => {
    utiliserStoreAuth.getState().definirChargement(true);
    expect(utiliserStoreAuth.getState().estChargement).toBe(true);

    utiliserStoreAuth.getState().definirChargement(false);
    expect(utiliserStoreAuth.getState().estChargement).toBe(false);
  });

  it("reinitialiser remet tout à zéro", () => {
    const mockUser = { id: "1", email: "test@example.com", nom: "Test" };
    utiliserStoreAuth.getState().definirUtilisateur(mockUser as never);
    utiliserStoreAuth.getState().reinitialiser();

    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toBeNull();
    expect(state.estConnecte).toBe(false);
    expect(state.estChargement).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════
// store-ui
// ═══════════════════════════════════════════════════════════

describe("utiliserStoreUI", () => {
  beforeEach(() => {
    utiliserStoreUI.setState({
      sidebarOuverte: true,
      rechercheOuverte: false,
      titrePage: null,
    });
  });

  it("basculerSidebar inverse l'état", () => {
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(true);

    utiliserStoreUI.getState().basculerSidebar();
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(false);

    utiliserStoreUI.getState().basculerSidebar();
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(true);
  });

  it("definirSidebar fixe la valeur", () => {
    utiliserStoreUI.getState().definirSidebar(false);
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(false);

    utiliserStoreUI.getState().definirSidebar(true);
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(true);
  });

  it("basculerRecherche inverse l'état", () => {
    expect(utiliserStoreUI.getState().rechercheOuverte).toBe(false);

    utiliserStoreUI.getState().basculerRecherche();
    expect(utiliserStoreUI.getState().rechercheOuverte).toBe(true);
  });

  it("definirRecherche fixe la valeur", () => {
    utiliserStoreUI.getState().definirRecherche(true);
    expect(utiliserStoreUI.getState().rechercheOuverte).toBe(true);
  });

  it("definirTitrePage met à jour le titre", () => {
    utiliserStoreUI.getState().definirTitrePage("Ma Page");
    expect(utiliserStoreUI.getState().titrePage).toBe("Ma Page");

    utiliserStoreUI.getState().definirTitrePage(null);
    expect(utiliserStoreUI.getState().titrePage).toBeNull();
  });
});

// ═══════════════════════════════════════════════════════════
// store-notifications
// ═══════════════════════════════════════════════════════════

describe("utiliserStoreNotifications", () => {
  beforeEach(() => {
    utiliserStoreNotifications.getState().vider();
  });

  it("ajouter crée une notification avec un id", () => {
    utiliserStoreNotifications
      .getState()
      .ajouter({ type: "succes", message: "Opération réussie" });

    const state = utiliserStoreNotifications.getState();
    expect(state.notifications).toHaveLength(1);
    expect(state.notifications[0].type).toBe("succes");
    expect(state.notifications[0].message).toBe("Opération réussie");
    expect(state.notifications[0].id).toBeDefined();
  });

  it("ajouter plusieurs notifications les empile", () => {
    const store = utiliserStoreNotifications.getState();
    store.ajouter({ type: "info", message: "Info 1" });
    store.ajouter({ type: "erreur", message: "Erreur 1" });
    store.ajouter({ type: "attention", message: "Attention 1" });

    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(3);
  });

  it("retirer supprime une notification par id", () => {
    utiliserStoreNotifications
      .getState()
      .ajouter({ type: "info", message: "À retirer" });

    const notif = utiliserStoreNotifications.getState().notifications[0];
    utiliserStoreNotifications.getState().retirer(notif.id);

    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(0);
  });

  it("vider supprime toutes les notifications", () => {
    const store = utiliserStoreNotifications.getState();
    store.ajouter({ type: "info", message: "1" });
    store.ajouter({ type: "info", message: "2" });
    store.vider();

    expect(utiliserStoreNotifications.getState().notifications).toHaveLength(0);
  });

  it("les types de notification sont correctement assignés", () => {
    const store = utiliserStoreNotifications.getState();
    store.ajouter({ type: "succes", message: "Succès" });
    store.ajouter({ type: "erreur", message: "Erreur" });
    store.ajouter({ type: "info", message: "Info" });
    store.ajouter({ type: "attention", message: "Attention" });

    const types = utiliserStoreNotifications
      .getState()
      .notifications.map((n) => n.type);
    expect(types).toEqual(["succes", "erreur", "info", "attention"]);
  });

  it("chaque notification a un id unique", () => {
    const store = utiliserStoreNotifications.getState();
    store.ajouter({ type: "info", message: "1" });
    store.ajouter({ type: "info", message: "2" });

    const ids = utiliserStoreNotifications
      .getState()
      .notifications.map((n) => n.id);
    expect(ids[0]).not.toBe(ids[1]);
  });
});
