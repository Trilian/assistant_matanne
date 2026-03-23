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
  return useQuery<T>({
    queryKey: cle,
    queryFn: fn,
    staleTime: DUREE_CACHE_MS,
    ...options,
  });
}

/**
 * Mutation wrapper avec invalidation automatique.
 * Usage: `utiliserMutation(mutationFn, { onSuccess: () => ... })`
 */
export function utiliserMutation<TData, TVariables>(
  fn: (variables: TVariables) => Promise<TData>,
  options?: Partial<UseMutationOptions<TData, Error, TVariables>>
) {
  return useMutation<TData, Error, TVariables>({
    mutationFn: fn,
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
