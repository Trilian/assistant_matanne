// ═══════════════════════════════════════════════════════════
// Contenu Principal — Wrapper avec fade-in au changement de page (Idée E)
// ═══════════════════════════════════════════════════════════

"use client";

import { usePathname } from "next/navigation";

/**
 * Enveloppe le contenu de la page avec une animation fade-in à chaque navigation.
 * La clé `pathname` force le re-montage du div à chaque changement de route.
 */
export function ContenuPrincipal({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <main
      className="flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6"
      id="contenu-principal"
    >
      <div key={pathname} className="animate-in fade-in duration-150">
        {children}
      </div>
    </main>
  );
}
