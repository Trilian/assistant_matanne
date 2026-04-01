// ═══════════════════════════════════════════════════════════
// Contenu Principal — Wrapper avec fade-in au changement de page (Idée E)
// ═══════════════════════════════════════════════════════════

"use client";

import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";

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
      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 8, filter: "blur(2px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -6, filter: "blur(1px)" }}
          transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
        >
          {children}
        </motion.div>
      </AnimatePresence>
    </main>
  );
}
