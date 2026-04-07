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
  }, [estConnecte, estChargement, estPublique, router]);

  // Routes publiques (/connexion, /inscription) : toujours afficher le formulaire
  if (estPublique) {
    return <>{children}</>;
  }

  // Routes protégées : spinner pendant le chargement ou en attendant la redirection
  if (estChargement || !estConnecte) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
