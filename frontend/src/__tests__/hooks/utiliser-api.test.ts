import { describe, expect, it, vi } from "vitest";
import {
  utiliserInvalidation,
  utiliserMutation,
  utiliserMutationAvecInvalidation,
  utiliserRequete,
  utiliserRequetePaginee,
} from "@/crochets/utiliser-api";

const invalidateQueries = vi.fn();

vi.mock("@tanstack/react-query", () => ({
  useQuery: vi.fn((opts) => {
    // Simuler des options par défaut
    const staleTime = opts.staleTime ?? 0;
    return {
      data: opts._mockData ?? { ok: true },
      isLoading: opts._mockLoading ?? false,
      error: opts._mockError ?? null,
      queryKey: opts.queryKey,
      _staleTime: staleTime,
    };
  }),
  useMutation: vi.fn((opts) => ({
    mutate: async (variables: unknown) => {
      const result = await opts.mutationFn(variables);
      opts.onSuccess?.(result, variables, undefined);
      return result;
    },
    isPending: false,
    _onError: opts.onError,
  })),
  useQueryClient: () => ({ invalidateQueries }),
}));

vi.mock("sonner", () => ({
  toast: { error: vi.fn() },
}));

describe("utiliser-api", () => {
  it("utiliserRequete expose alias donnees/chargement/erreur", () => {
    const resultat = utiliserRequete(["x"], async () => ({ ok: true }));

    expect(resultat.donnees).toEqual({ ok: true });
    expect(resultat.chargement).toBe(false);
    expect(resultat.erreur).toBeNull();
  });

  it("utiliserMutation retourne un objet mutation", () => {
    const mutation = utiliserMutation(async () => ({ id: 1 }));
    expect(typeof mutation.mutate).toBe("function");
  });

  it("utiliserMutationAvecInvalidation invalide les clés après succès", async () => {
    const mutation = utiliserMutationAvecInvalidation(
      async () => ({ ok: true }),
      [["a"], ["b"]]
    );

    await mutation.mutate(undefined);

    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["a"] });
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["b"] });
  });

  it("utiliserMutation inclut un onError par défaut pour les toasts", () => {
    const mutation = utiliserMutation(async () => ({ id: 1 }));
    // Le useMutation mock expose _onError
    expect(typeof (mutation as Record<string, unknown>)._onError).toBe("function");
  });

  it("utiliserInvalidation retourne une fonction", () => {
    const invalider = utiliserInvalidation();
    expect(typeof invalider).toBe("function");
  });

  it("utiliserInvalidation appelle invalidateQueries avec la bonne clé", () => {
    const invalider = utiliserInvalidation();
    invalider(["recettes"]);
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["recettes"] });
  });

  it("utiliserRequetePaginee inclut la page dans la queryKey", () => {
    const resultat = utiliserRequetePaginee(["items"], async () => ({ items: [] }), 3);
    expect(resultat.queryKey).toEqual(["items", 3]);
  });

  it("utiliserMutationAvecInvalidation appelle onSuccess personnalisé en plus", async () => {
    const onSuccessCustom = vi.fn();
    const mutation = utiliserMutationAvecInvalidation(
      async () => ({ ok: true }),
      [["c"]],
      { onSuccess: onSuccessCustom }
    );

    await mutation.mutate(undefined);

    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ["c"] });
    expect(onSuccessCustom).toHaveBeenCalled();
  });
});
