// Tests API auth — connexion, inscription, profil, 2FA

import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  connecter,
  inscrire,
  obtenirProfil,
  deconnecter,
  activer2FA,
  statut2FA,
  rafraichirToken,
} from "@/bibliotheque/api/auth";

const api = vi.mocked(clientApi);

beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal("localStorage", {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
  });
});

describe("connecter", () => {
  it("appelle POST /auth/login et retourne le token", async () => {
    const resp = { access_token: "jwt123", token_type: "bearer" };
    api.post.mockResolvedValueOnce({ data: resp });

    const result = await connecter({ email: "test@test.com", mot_de_passe: "secret" });

    expect(api.post).toHaveBeenCalledWith("/auth/login", {
      email: "test@test.com",
      password: "secret",
    });
    expect(result.access_token).toBe("jwt123");
  });

  it("gère la réponse 2FA", async () => {
    api.post.mockResolvedValueOnce({ data: { requires_2fa: true, temp_token: "tmp" } });

    const result = await connecter({ email: "a@b.com", mot_de_passe: "x" });

    expect(result.requires_2fa).toBe(true);
    expect(result.temp_token).toBe("tmp");
  });
});

describe("inscrire", () => {
  it("appelle POST /auth/register", async () => {
    const resp = { access_token: "new", token_type: "bearer" };
    api.post.mockResolvedValueOnce({ data: resp });

    const result = await inscrire({ email: "new@test.com", mot_de_passe: "pass", nom: "Test" });

    expect(api.post).toHaveBeenCalledWith("/auth/register", {
      email: "new@test.com",
      password: "pass",
      nom: "Test",
    });
    expect(result.access_token).toBe("new");
  });
});

describe("obtenirProfil", () => {
  it("appelle GET /auth/me", async () => {
    const user = { id: "1", email: "user@test.com", nom: "User" };
    api.get.mockResolvedValueOnce({ data: user });

    const result = await obtenirProfil();

    expect(api.get).toHaveBeenCalledWith("/auth/me");
    expect(result.email).toBe("user@test.com");
  });
});

describe("deconnecter", () => {
  it("supprime le token du localStorage", () => {
    deconnecter();

    expect(localStorage.removeItem).toHaveBeenCalledWith("access_token");
  });
});

describe("activer2FA", () => {
  it("appelle POST /auth/2fa/enable", async () => {
    const resp = { secret: "ABCD", qr_code: "data:...", backup_codes: ["111", "222"] };
    api.post.mockResolvedValueOnce({ data: resp });

    const result = await activer2FA();

    expect(api.post).toHaveBeenCalledWith("/auth/2fa/enable");
    expect(result.backup_codes).toHaveLength(2);
  });
});

describe("statut2FA", () => {
  it("appelle GET /auth/2fa/status", async () => {
    api.get.mockResolvedValueOnce({ data: { enabled: true, backup_codes_remaining: 5 } });

    const result = await statut2FA();

    expect(result.enabled).toBe(true);
  });
});

describe("rafraichirToken", () => {
  it("appelle POST /auth/refresh", async () => {
    api.post.mockResolvedValueOnce({ data: { access_token: "refreshed" } });

    const result = await rafraichirToken();

    expect(api.post).toHaveBeenCalledWith("/auth/refresh");
    expect(result.access_token).toBe("refreshed");
  });
});
