import { describe, it, expect, beforeEach } from "vitest";
import { utiliserStoreUI } from "@/magasins/store-ui";

describe("Store UI (Zustand)", () => {
  beforeEach(() => {
    // Reset store between tests
    utiliserStoreUI.setState({
      sidebarOuverte: true,
      rechercheOuverte: false,
    });
  });

  it("sidebar ouverte par défaut", () => {
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(true);
  });

  it("basculerSidebar ferme la sidebar", () => {
    utiliserStoreUI.getState().basculerSidebar();
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(false);
  });

  it("basculerSidebar toggle on/off", () => {
    utiliserStoreUI.getState().basculerSidebar();
    utiliserStoreUI.getState().basculerSidebar();
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(true);
  });

  it("definirSidebar force la valeur", () => {
    utiliserStoreUI.getState().definirSidebar(false);
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(false);
    utiliserStoreUI.getState().definirSidebar(true);
    expect(utiliserStoreUI.getState().sidebarOuverte).toBe(true);
  });

  it("recherche fermée par défaut", () => {
    expect(utiliserStoreUI.getState().rechercheOuverte).toBe(false);
  });

  it("basculerRecherche ouvre la recherche", () => {
    utiliserStoreUI.getState().basculerRecherche();
    expect(utiliserStoreUI.getState().rechercheOuverte).toBe(true);
  });

  it("definirRecherche force la valeur", () => {
    utiliserStoreUI.getState().definirRecherche(true);
    expect(utiliserStoreUI.getState().rechercheOuverte).toBe(true);
  });
});
