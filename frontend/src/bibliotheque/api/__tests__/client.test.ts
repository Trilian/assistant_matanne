// Tests client API — instance axios, intercepteurs JWT

import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock axios before importing client
vi.mock("axios", () => {
  const interceptors = {
    request: { use: vi.fn() },
    response: { use: vi.fn() },
  };
  const instance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors,
    defaults: { headers: { common: {} } },
  };
  return {
    default: {
      create: vi.fn().mockReturnValue(instance),
      post: vi.fn(),
    },
  };
});

vi.mock("@/bibliotheque/constantes", () => ({
  URL_API: "http://localhost:8000",
  PREFIXE_API: "/api/v1",
}));

describe("clientApi", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.resetModules();
  });

  it("crée une instance axios avec la bonne baseURL", async () => {
    const axios = (await import("axios")).default;
    await import("@/bibliotheque/api/client");

    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        baseURL: "http://localhost:8000/api/v1",
        timeout: 30_000,
      })
    );
  });

  it("enregistre un intercepteur de requête", async () => {
    const axios = (await import("axios")).default;
    const instance = axios.create();
    await import("@/bibliotheque/api/client");

    expect(instance.interceptors.request.use).toHaveBeenCalled();
  });

  it("enregistre un intercepteur de réponse", async () => {
    const axios = (await import("axios")).default;
    const instance = axios.create();
    await import("@/bibliotheque/api/client");

    expect(instance.interceptors.response.use).toHaveBeenCalled();
  });

  it("l'intercepteur requête ajoute le Bearer token", async () => {
    vi.stubGlobal("localStorage", {
      getItem: vi.fn().mockReturnValue("my-jwt-token"),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });

    const axios = (await import("axios")).default;
    const instance = axios.create();
    await import("@/bibliotheque/api/client");

    // Get the request interceptor callback
    const requestInterceptor = vi.mocked(instance.interceptors.request.use).mock.calls[0]?.[0];
    if (typeof requestInterceptor === "function") {
      const config = { headers: {} as Record<string, string> };
      const result = requestInterceptor(config as never);
      expect((result as { headers: Record<string, string> }).headers.Authorization).toBe("Bearer my-jwt-token");
    }
  });
});
