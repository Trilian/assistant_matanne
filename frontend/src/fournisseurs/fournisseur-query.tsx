// ═══════════════════════════════════════════════════════════
// Fournisseur TanStack Query
// ═══════════════════════════════════════════════════════════

"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";
import { DUREE_CACHE_MS } from "@/bibliotheque/constantes";

export function FournisseurQuery({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: DUREE_CACHE_MS,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
