// ═══════════════════════════════════════════════════════════
// Hook useLocalStorage
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useEffect, useCallback } from "react";

/**
 * useState synchronisé avec localStorage.
 * Usage: `const [theme, setTheme] = utiliserStockageLocal("theme", "light")`
 */
export function utiliserStockageLocal<T>(cle: string, valeurDefaut: T) {
  const [valeur, setValeur] = useState<T>(() => {
    if (typeof window === "undefined") return valeurDefaut;
    try {
      const stocke = window.localStorage.getItem(cle);
      return stocke ? (JSON.parse(stocke) as T) : valeurDefaut;
    } catch {
      return valeurDefaut;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(cle, JSON.stringify(valeur));
    } catch {
      // Quota dépassé ou indisponible
    }
  }, [cle, valeur]);

  const reinitialiser = useCallback(() => {
    setValeur(valeurDefaut);
    window.localStorage.removeItem(cle);
  }, [cle, valeurDefaut]);

  return [valeur, setValeur, reinitialiser] as const;
}
