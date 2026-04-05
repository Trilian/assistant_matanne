// Tests hook utiliser-auth — chargement profil, déconnexion

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";

// Mock the auth API
vi.mock("@/bibliotheque/api/auth", () => ({
  obtenirProfil: vi.fn(),
  deconnecter: vi.fn(),
}));

// Mock the store
const mockStore = {
  utilisateur: null as { id: string; email: string } | null,
  estConnecte: false,
  estChargement: true,
  definirUtilisateur: vi.fn(),
  reinitialiser: vi.fn(),
};

vi.mock("@/magasins/store-auth", () => ({
  utiliserStoreAuth: vi.fn(() => mockStore),
}));

import { obtenirProfil, deconnecter as apiDeconnecter } from "@/bibliotheque/api/auth";
import { utiliserAuth } from "@/crochets/utiliser-auth";

beforeEach(() => {
  vi.clearAllMocks();
  mockStore.utilisateur = null;
  mockStore.estConnecte = false;
  mockStore.estChargement = true;
  vi.stubGlobal("localStorage", {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
  });
});

describe("utiliserAuth", () => {
  it("charge le profil quand un token existe", async () => {
    vi.mocked(localStorage.getItem).mockReturnValue("jwt-token");
    const user = { id: "1", email: "test@test.com" };
    vi.mocked(obtenirProfil).mockResolvedValueOnce(user as never);

    renderHook(() => utiliserAuth());

    await waitFor(() => {
      expect(obtenirProfil).toHaveBeenCalledOnce();
      expect(mockStore.definirUtilisateur).toHaveBeenCalledWith(user);
    });
  });

  it("ne charge pas le profil sans token", () => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);

    renderHook(() => utiliserAuth());

    expect(obtenirProfil).not.toHaveBeenCalled();
    expect(mockStore.definirUtilisateur).toHaveBeenCalledWith(null);
  });

  it("supprime le token en cas d'erreur profil", async () => {
    vi.mocked(localStorage.getItem).mockReturnValue("bad-token");
    vi.mocked(obtenirProfil).mockRejectedValueOnce(new Error("401"));

    renderHook(() => utiliserAuth());

    await waitFor(() => {
      expect(localStorage.removeItem).toHaveBeenCalledWith("access_token");
      expect(mockStore.definirUtilisateur).toHaveBeenCalledWith(null);
    });
  });

  it("deconnecter reinitialise le store et appelle l'API", () => {
    mockStore.utilisateur = { id: "1", email: "a@b.com" };
    mockStore.estConnecte = true;

    const { result } = renderHook(() => utiliserAuth());

    act(() => result.current.deconnecter());

    expect(mockStore.reinitialiser).toHaveBeenCalledOnce();
    expect(apiDeconnecter).toHaveBeenCalledOnce();
  });

  it("expose les propriétés attendues", () => {
    const { result } = renderHook(() => utiliserAuth());

    expect(result.current).toHaveProperty("utilisateur");
    expect(result.current).toHaveProperty("user");
    expect(result.current).toHaveProperty("estConnecte");
    expect(result.current).toHaveProperty("estChargement");
    expect(result.current).toHaveProperty("deconnecter");
  });
});
