import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { utiliserAuth } from "@/crochets/utiliser-auth";

const definirUtilisateur = vi.fn();
const reinitialiser = vi.fn();
const apiDeconnecter = vi.fn();

vi.mock("@/magasins/store-auth", () => ({
  utiliserStoreAuth: () => ({
    utilisateur: null,
    estConnecte: false,
    estChargement: false,
    definirUtilisateur,
    reinitialiser,
  }),
}));

vi.mock("@/bibliotheque/api/auth", () => ({
  obtenirProfil: vi.fn(async () => ({ id: "u1", role: "admin" })),
  deconnecter: () => apiDeconnecter(),
}));

describe("utiliserAuth", () => {
  beforeEach(() => {
    localStorage.clear();
    definirUtilisateur.mockReset();
    reinitialiser.mockReset();
    apiDeconnecter.mockReset();
  });

  it("met utilisateur à null sans token", () => {
    renderHook(() => utiliserAuth());
    expect(definirUtilisateur).toHaveBeenCalledWith(null);
  });

  it("expose deconnecter et réinitialise la session", () => {
    const { result } = renderHook(() => utiliserAuth());
    result.current.deconnecter();

    expect(reinitialiser).toHaveBeenCalled();
    expect(apiDeconnecter).toHaveBeenCalled();
  });
});
