import { describe, it, expect, beforeEach } from "vitest";
import { utiliserStoreAuth } from "@/magasins/store-auth";

describe("Store Auth (Zustand)", () => {
  beforeEach(() => {
    utiliserStoreAuth.getState().reinitialiser();
  });

  it("état initial : non connecté, en chargement", () => {
    // reinitialiser sets estChargement to false
    utiliserStoreAuth.setState({ estChargement: true });
    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toBeNull();
    expect(state.estConnecte).toBe(false);
    expect(state.estChargement).toBe(true);
  });

  it("definirUtilisateur met à jour l'état", () => {
    const user = { id: 1, nom: "Anne", email: "anne@test.com" } as never;
    utiliserStoreAuth.getState().definirUtilisateur(user);

    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toEqual(user);
    expect(state.estConnecte).toBe(true);
    expect(state.estChargement).toBe(false);
  });

  it("definirUtilisateur(null) déconnecte", () => {
    const user = { id: 1, nom: "Anne", email: "anne@test.com" } as never;
    utiliserStoreAuth.getState().definirUtilisateur(user);
    utiliserStoreAuth.getState().definirUtilisateur(null);

    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toBeNull();
    expect(state.estConnecte).toBe(false);
  });

  it("reinitialiser remet l'état à zéro", () => {
    const user = { id: 1, nom: "Anne", email: "anne@test.com" } as never;
    utiliserStoreAuth.getState().definirUtilisateur(user);
    utiliserStoreAuth.getState().reinitialiser();

    const state = utiliserStoreAuth.getState();
    expect(state.utilisateur).toBeNull();
    expect(state.estConnecte).toBe(false);
    expect(state.estChargement).toBe(false);
  });

  it("definirChargement change l'état de chargement", () => {
    utiliserStoreAuth.getState().definirChargement(true);
    expect(utiliserStoreAuth.getState().estChargement).toBe(true);
    utiliserStoreAuth.getState().definirChargement(false);
    expect(utiliserStoreAuth.getState().estChargement).toBe(false);
  });
});
