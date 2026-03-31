import { describe, expect, it, vi } from "vitest";
import { utiliserMutation, utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";

const invalidateQueries = vi.fn();

vi.mock("@tanstack/react-query", () => ({
  useQuery: vi.fn(() => ({ data: { ok: true }, isLoading: false, error: null })),
  useMutation: vi.fn((opts) => ({
    mutate: async (variables: unknown) => {
      const result = await opts.mutationFn(variables);
      opts.onSuccess?.(result, variables, undefined);
      return result;
    },
    isPending: false,
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
});
