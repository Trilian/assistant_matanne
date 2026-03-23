// ═══════════════════════════════════════════════════════════
// Fournisseur Auth — Protège les routes authentifiées
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { utiliserAuth } from "@/hooks/utiliser-auth";

const ROUTES_PUBLIQUES = ["/connexion", "/inscription"];

export function FournisseurAuth({ children }: { children: ReactNode }) {
  const { estConnecte, estChargement } = utiliserAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (estChargement) return;

    const estPublique = ROUTES_PUBLIQUES.some((r) => pathname.startsWith(r));

    if (!estConnecte && !estPublique) {
      router.replace("/connexion");
    } else if (estConnecte && estPublique) {
      router.replace("/");
    }
  }, [estConnecte, estChargement, pathname, router]);

  if (estChargement) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
