// Tests hooks — utiliser-auth, utiliser-delai, utiliser-stockage-local, use-mobile

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";

// ─── utiliser-delai ───────────────────────────────────────

describe("utiliserDelai", () => {
  beforeEach(() => vi.useFakeTimers());

  it("retourne la valeur initiale immédiatement", async () => {
    const { utiliserDelai } = await import("@/crochets/utiliser-delai");
    const { result } = renderHook(() => utiliserDelai("hello", 300));
    expect(result.current).toBe("hello");
  });

  it("retarde la mise à jour de la valeur", async () => {
    const { utiliserDelai } = await import("@/crochets/utiliser-delai");
    const { result, rerender } = renderHook(
      ({ val }) => utiliserDelai(val, 300),
      { initialProps: { val: "a" } }
    );

    rerender({ val: "b" });
    expect(result.current).toBe("a");

    act(() => vi.advanceTimersByTime(300));
    expect(result.current).toBe("b");
  });

  afterEach(() => vi.useRealTimers());
});

// ─── utiliser-stockage-local ──────────────────────────────

describe("utiliserStockageLocal", () => {
  beforeEach(() => {
    vi.stubGlobal("localStorage", {
      getItem: vi.fn().mockReturnValue(null),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    });
  });

  it("retourne la valeur par défaut si localStorage vide", async () => {
    const { utiliserStockageLocal } = await import("@/crochets/utiliser-stockage-local");
    const { result } = renderHook(() => utiliserStockageLocal("theme", "light"));
    expect(result.current[0]).toBe("light");
  });

  it("lit la valeur depuis localStorage", async () => {
    vi.mocked(localStorage.getItem).mockReturnValue(JSON.stringify("dark"));
    const { utiliserStockageLocal } = await import("@/crochets/utiliser-stockage-local");
    const { result } = renderHook(() => utiliserStockageLocal("theme", "light"));
    expect(result.current[0]).toBe("dark");
  });

  it("met à jour la valeur", async () => {
    const { utiliserStockageLocal } = await import("@/crochets/utiliser-stockage-local");
    const { result } = renderHook(() => utiliserStockageLocal("count", 0));

    act(() => result.current[1](42));
    expect(result.current[0]).toBe(42);
  });

  it("reinitialiser supprime la clé", async () => {
    const { utiliserStockageLocal } = await import("@/crochets/utiliser-stockage-local");
    const { result } = renderHook(() => utiliserStockageLocal("key", "val"));

    act(() => result.current[2]());
    expect(result.current[0]).toBe("val");
    expect(localStorage.removeItem).toHaveBeenCalledWith("key");
  });
});

// ─── use-mobile ───────────────────────────────────────────

describe("useIsMobile", () => {
  it("retourne false pour fenêtre large", async () => {
    Object.defineProperty(window, "innerWidth", { value: 1024, writable: true });
    Object.defineProperty(window, "matchMedia", {
      value: vi.fn().mockReturnValue({
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }),
      writable: true,
    });

    const { useIsMobile } = await import("@/crochets/use-mobile");
    const { result } = renderHook(() => useIsMobile());

    await waitFor(() => expect(result.current).toBe(false));
  });

  it("retourne true pour fenêtre mobile", async () => {
    Object.defineProperty(window, "innerWidth", { value: 375, writable: true });
    Object.defineProperty(window, "matchMedia", {
      value: vi.fn().mockReturnValue({
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }),
      writable: true,
    });

    // Clear module cache to re-run with new width
    vi.resetModules();
    const { useIsMobile } = await import("@/crochets/use-mobile");
    const { result } = renderHook(() => useIsMobile());

    await waitFor(() => expect(result.current).toBe(true));
  });
});
