/**
 * Tests unitaires pour les hooks React custom (P2-16).
 *
 * Couvre:
 * - utiliserAuth (authentification, déconnexion)
 * - utiliserApi (requêtes TanStack Query wrappers)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook } from "@testing-library/react";

// ═══════════════════════════════════════════════════════════
// Mock providers
// ═══════════════════════════════════════════════════════════

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    refresh: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock sonner toast
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
}));

// Mock auth API
vi.mock("@/bibliotheque/api/auth", () => ({
  obtenirProfil: vi.fn().mockResolvedValue({ id: "1", email: "test@test.com" }),
  deconnecter: vi.fn(),
  connecter: vi.fn().mockResolvedValue({ access_token: "mock-token" }),
}));

// ═══════════════════════════════════════════════════════════
// utiliserAuth
// ═══════════════════════════════════════════════════════════

describe("utiliserAuth", () => {
  beforeEach(() => {
    vi.resetModules();
    // Mock localStorage
    const storage: Record<string, string> = {};
    vi.stubGlobal("localStorage", {
      getItem: vi.fn((key: string) => storage[key] ?? null),
      setItem: vi.fn((key: string, value: string) => {
        storage[key] = value;
      }),
      removeItem: vi.fn((key: string) => {
        delete storage[key];
      }),
      clear: vi.fn(() => {
        Object.keys(storage).forEach((k) => delete storage[k]);
      }),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("retourne estConnecte false sans token", async () => {
    const { utiliserStoreAuth } = await import("@/magasins/store-auth");
    utiliserStoreAuth.getState().reinitialiser();

    const { utiliserAuth } = await import("@/crochets/utiliser-auth");

    const { result } = renderHook(() => utiliserAuth());

    // Initialement non connecté
    expect(result.current.estConnecte).toBe(false);
  });

  it("expose la fonction deconnecter", async () => {
    const { utiliserAuth } = await import("@/crochets/utiliser-auth");

    const { result } = renderHook(() => utiliserAuth());

    expect(result.current.deconnecter).toBeDefined();
    expect(typeof result.current.deconnecter).toBe("function");
  });

  it("retourne user comme alias de utilisateur", async () => {
    const { utiliserAuth } = await import("@/crochets/utiliser-auth");

    const { result } = renderHook(() => utiliserAuth());

    expect(result.current.user).toBe(result.current.utilisateur);
  });
});

// ═══════════════════════════════════════════════════════════
// utiliserApi hooks - type checks
// ═══════════════════════════════════════════════════════════

describe("utiliserApi exports", () => {
  it("exporte utiliserRequete", async () => {
    const api = await import("@/crochets/utiliser-api");
    expect(api.utiliserRequete).toBeDefined();
    expect(typeof api.utiliserRequete).toBe("function");
  });

  it("exporte utiliserMutation", async () => {
    const api = await import("@/crochets/utiliser-api");
    expect(api.utiliserMutation).toBeDefined();
    expect(typeof api.utiliserMutation).toBe("function");
  });

  it("exporte utiliserInvalidation", async () => {
    const api = await import("@/crochets/utiliser-api");
    expect(api.utiliserInvalidation).toBeDefined();
    expect(typeof api.utiliserInvalidation).toBe("function");
  });

  it("exporte utiliserMutationAvecInvalidation", async () => {
    const api = await import("@/crochets/utiliser-api");
    expect(api.utiliserMutationAvecInvalidation).toBeDefined();
    expect(typeof api.utiliserMutationAvecInvalidation).toBe("function");
  });

  it("exporte utiliserRequetePaginee", async () => {
    const api = await import("@/crochets/utiliser-api");
    expect(api.utiliserRequetePaginee).toBeDefined();
    expect(typeof api.utiliserRequetePaginee).toBe("function");
  });
});
