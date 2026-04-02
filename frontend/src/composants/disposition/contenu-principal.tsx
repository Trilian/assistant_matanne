// ═══════════════════════════════════════════════════════════
// Contenu Principal — Wrapper avec fade-in au changement de page (Idée E)
// ═══════════════════════════════════════════════════════════

"use client";

import { useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Enveloppe le contenu de la page avec une animation fade-in à chaque navigation.
 * La clé `pathname` force le re-montage du div à chaque changement de route.
 */
export function ContenuPrincipal({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const queryClient = useQueryClient();
  const mainRef = useRef<HTMLElement | null>(null);
  const startYRef = useRef<number | null>(null);
  const [distanceTirage, setDistanceTirage] = useState(0);
  const [rafraichissementEnCours, setRafraichissementEnCours] = useState(false);

  const onTouchStart = (event: React.TouchEvent<HTMLElement>) => {
    if (window.innerWidth >= 768) return;
    if ((mainRef.current?.scrollTop ?? 1) > 0 || rafraichissementEnCours) return;
    startYRef.current = event.touches[0].clientY;
  };

  const onTouchMove = (event: React.TouchEvent<HTMLElement>) => {
    if (startYRef.current === null) return;
    if ((mainRef.current?.scrollTop ?? 1) > 0) return;

    const delta = event.touches[0].clientY - startYRef.current;
    if (delta <= 0) {
      setDistanceTirage(0);
      return;
    }

    setDistanceTirage(Math.min(96, delta * 0.55));
  };

  const onTouchEnd = async () => {
    if (startYRef.current === null) return;
    startYRef.current = null;

    if (distanceTirage >= 70 && !rafraichissementEnCours) {
      setRafraichissementEnCours(true);
      setDistanceTirage(56);
      await queryClient.invalidateQueries();
      setRafraichissementEnCours(false);
    }

    setDistanceTirage(0);
  };

  return (
    <main
      ref={mainRef}
      className="relative flex-1 overflow-y-auto p-4 md:p-6 pb-24 md:pb-6"
      id="contenu-principal"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      <div
        className="pointer-events-none absolute left-1/2 top-2 z-20 -translate-x-1/2 rounded-full border bg-background/90 px-3 py-1 text-xs text-muted-foreground shadow-sm transition-all"
        style={{
          opacity: distanceTirage > 0 || rafraichissementEnCours ? 1 : 0,
          transform: `translate(-50%, ${Math.min(distanceTirage, 42)}px)`,
        }}
      >
        {rafraichissementEnCours ? "Mise a jour..." : "Tirer pour rafraichir"}
      </div>

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
