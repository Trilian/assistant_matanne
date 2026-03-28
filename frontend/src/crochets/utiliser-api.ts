// ═══════════════════════════════════════════════════════════
// Hook useApi — Helpers TanStack Query
// ═══════════════════════════════════════════════════════════

"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { DUREE_CACHE_MS } from "@/bibliotheque/constantes";

/**
 * Query wrapper avec cache par défaut de 5 minutes.
 * Usage: `utiliserRequete(["recettes"], listerRecettes)`
 */
export function utiliserRequete<T>(
  cle: string[],
  fn: () => Promise<T>,
  options?: Partial<UseQueryOptions<T>>
) {
  const requete = useQuery<T>({
    queryKey: cle,
    queryFn: fn,
    staleTime: DUREE_CACHE_MS,
    ...options,
  });

  return {
    ...requete,
    donnees: requete.data,
    chargement: requete.isLoading,
    erreur: requete.error,
  };
}

/**
 * Mutation wrapper avec invalidation automatique.
 * Usage: `utiliserMutation(mutationFn, { onSuccess: () => ... })`
 */
export function utiliserMutation<TData, TVariables = void>(
  fn: (variables: TVariables) => Promise<TData>,
  options?: Partial<UseMutationOptions<TData, Error, TVariables>>
) {
  return useMutation<TData, Error, TVariables>({
    mutationFn: fn,
    onError: (error) => toast.error(error.message || "Une erreur est survenue"),
    ...options,
  });
}

/**
 * Hook pour invalider le cache d'une clé.
 * Usage: `const invalider = utiliserInvalidation(); invalider(["recettes"])`
 */
export function utiliserInvalidation() {
  const queryClient = useQueryClient();
  return (cle: string[]) => queryClient.invalidateQueries({ queryKey: cle });
}

/**
 * Mutation avec invalidation automatique après succès.
 * Usage: `utiliserMutationAvecInvalidation(creerRecette, ["recettes"])`
 */
export function utiliserMutationAvecInvalidation<TData, TVariables>(
  fn: (variables: TVariables) => Promise<TData>,
  clesAInvalider: string[][],
  options?: Partial<UseMutationOptions<TData, Error, TVariables>>
) {
  const queryClient = useQueryClient();
  return useMutation<TData, Error, TVariables>({
    mutationFn: fn,
    onSuccess: (...args) => {
      for (const cle of clesAInvalider) {
        queryClient.invalidateQueries({ queryKey: cle });
      }
      options?.onSuccess?.(...args);
    },
    ...options,
    // Ré-appliquer onSuccess après spread pour ne pas l'écraser
  });
}

/**
 * Query paginée avec paramètres de page.
 * Usage: `utiliserRequetePaginee(["recettes"], (p) => listerRecettes(p), page)`
 */
export function utiliserRequetePaginee<T>(
  cleBase: string[],
  fn: (page: number) => Promise<T>,
  page: number,
  options?: Partial<UseQueryOptions<T>>
) {
  return useQuery<T>({
    queryKey: [...cleBase, page],
    queryFn: () => fn(page),
    staleTime: DUREE_CACHE_MS,
    ...options,
  });
}
