"use client";

import { useEffect, useMemo, useRef } from "react";

interface OptionsBrouillonAuto<T> {
  cle: string;
  valeur: T;
  actif?: boolean;
  delaiMs?: number;
  version?: number;
}

interface ResultatBrouillonAuto<T> {
  valeurInitiale: T | null;
  effacerBrouillon: () => void;
}

interface EnveloppeBrouillon<T> {
  version: number;
  valeur: T;
  horodatage: string;
}

/**
 * Hook de sauvegarde automatique de brouillon dans localStorage.
 * Persiste la valeur après un délai configurable et restaure au montage.
 * @param options - Clé localStorage, valeur à sauvegarder, délai debounce
 * @returns Valeur initiale restaurée et fonction d'effacement
 */
export function utiliserBrouillonAuto<T>({
  cle,
  valeur,
  actif = true,
  delaiMs = 600,
  version = 1,
}: OptionsBrouillonAuto<T>): ResultatBrouillonAuto<T> {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const valeurInitiale = useMemo(() => {
    if (typeof window === "undefined") {
      return null;
    }

    try {
      const brut = window.localStorage.getItem(cle);
      if (!brut) {
        return null;
      }

      const parsed = JSON.parse(brut) as EnveloppeBrouillon<T>;
      if (!parsed || parsed.version !== version) {
        return null;
      }

      return parsed.valeur ?? null;
    } catch {
      return null;
    }
  }, [cle, version]);

  useEffect(() => {
    if (!actif || typeof window === "undefined") {
      return;
    }

    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      try {
        const payload: EnveloppeBrouillon<T> = {
          version,
          valeur,
          horodatage: new Date().toISOString(),
        };
        window.localStorage.setItem(cle, JSON.stringify(payload));
      } catch {
        // localStorage indisponible ou quota atteint
      }
    }, delaiMs);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [actif, cle, delaiMs, valeur, version]);

  return {
    valeurInitiale,
    effacerBrouillon: () => {
      if (typeof window !== "undefined") {
        window.localStorage.removeItem(cle);
      }
    },
  };
}