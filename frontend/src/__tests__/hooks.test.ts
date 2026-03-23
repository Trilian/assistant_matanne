// ═══════════════════════════════════════════════════════════
// Tests hooks — utiliserRequete, utiliserMutation, utiliserInvalidation
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(
      QueryClientProvider,
      { client: queryClient },
      children
    );
  };
}

describe("utiliserRequete", () => {
  it("appelle la fonction et retourne les données", async () => {
    const mockData = [{ id: 1, nom: "Tomates" }];
    const fn = vi.fn().mockResolvedValue(mockData);

    const { result } = renderHook(() => utiliserRequete(["test"], fn), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(fn).toHaveBeenCalledOnce();
    expect(result.current.data).toEqual(mockData);
  });

  it("gère les erreurs", async () => {
    const fn = vi.fn().mockRejectedValue(new Error("fail"));

    const { result } = renderHook(() => utiliserRequete(["err"], fn, { retry: false }), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error?.message).toBe("fail");
  });
});

describe("utiliserMutation", () => {
  it("exécute la mutation et retourne le résultat", async () => {
    const fn = vi.fn().mockResolvedValue({ id: 1 });

    const { result } = renderHook(() => utiliserMutation(fn), {
      wrapper: createWrapper(),
    });

    result.current.mutate("test-input");

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(fn).toHaveBeenCalledWith("test-input");
    expect(result.current.data).toEqual({ id: 1 });
  });

  it("appelle onSuccess après une mutation réussie", async () => {
    const fn = vi.fn().mockResolvedValue({ ok: true });
    const onSuccess = vi.fn();

    const { result } = renderHook(
      () => utiliserMutation(fn, { onSuccess }),
      { wrapper: createWrapper() }
    );

    result.current.mutate(undefined);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(onSuccess).toHaveBeenCalled();
  });
});

describe("utiliserInvalidation", () => {
  it("retourne une fonction", () => {
    const { result } = renderHook(() => utiliserInvalidation(), {
      wrapper: createWrapper(),
    });

    expect(typeof result.current).toBe("function");
  });
});
