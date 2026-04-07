// ═══════════════════════════════════════════════════════════
// Fournisseur Auth — Protège les routes authentifiées
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { utiliserAuth } from "@/crochets/utiliser-auth";

const ROUTES_PUBLIQUES = ["/connexion", "/inscription"];

export function FournisseurAuth({ children }: { children: ReactNode }) {
  const { estConnecte, estChargement } = utiliserAuth();
  const pathname = usePathname();
  const router = useRouter();

  const estPublique = ROUTES_PUBLIQUES.some((r) => pathname.startsWith(r));

  useEffect(() => {
    if (estChargement) return;

    if (!estConnecte && !estPublique) {
      router.replace("/connexion");
    } else if (estConnecte && estPublique) {
      router.replace("/");
    }
  }, [estConnecte, estChargement, estPublique, pathname, router]);

  // Sur les routes publiques (/connexion, /inscription), on affiche toujours le formulaire
  // sans bloquer sur le spinner — la redirection se fera via le useEffect si déjà connecté.
  if (estChargement && !estPublique) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
