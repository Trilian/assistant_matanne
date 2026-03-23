// ═══════════════════════════════════════════════════════════
// Hook useDebounce — Délai de saisie
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useEffect } from "react";

/**
 * Retourne la valeur après un délai (debounce).
 * Usage: `const termeRecherche = utiliserDelai(saisie, 300)`
 */
export function utiliserDelai<T>(valeur: T, delaiMs = 300): T {
  const [valeurRetardee, setValeurRetardee] = useState(valeur);

  useEffect(() => {
    const timer = setTimeout(() => setValeurRetardee(valeur), delaiMs);
    return () => clearTimeout(timer);
  }, [valeur, delaiMs]);

  return valeurRetardee;
}
