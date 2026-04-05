"use client";

import { useCallback } from "react";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";

export interface ContexteModeInvites {
  actif: boolean;
  nbInvites: number;
  occasion: string;
  evenements: string[];
}

export const CONTEXTE_MODE_INVITES_DEFAUT: ContexteModeInvites = {
  actif: false,
  nbInvites: 0,
  occasion: "",
  evenements: [],
};

function nettoyerTexte(valeur: string): string {
  return valeur.trim().replace(/\s+/g, " ");
}

/**
 * Normalise et valide un contexte de mode invités (nb invités 0-20, occasion, événements uniques max 6).
 * @param contexte - Contexte partiel à normaliser
 * @returns Contexte normalisé complet
 */
export function normaliserContexteModeInvites(
  contexte?: Partial<ContexteModeInvites>
): ContexteModeInvites {
  return {
    actif: Boolean(contexte?.actif),
    nbInvites: Math.max(0, Math.min(20, Number(contexte?.nbInvites ?? 0) || 0)),
    occasion: nettoyerTexte(contexte?.occasion ?? ""),
    evenements: Array.from(
      new Set((contexte?.evenements ?? []).map((item) => nettoyerTexte(item)).filter(Boolean))
    ).slice(0, 6),
  };
}

/**
 * Hook de gestion du mode invités pour les courses — persiste dans localStorage.
 * @returns {contexte, mettreAJour, reinitialiser}
 */
export function utiliserModeInvites() {
  const [valeur, setValeur, reinitialiserStockage] = utiliserStockageLocal<ContexteModeInvites>(
    "cuisine-mode-invites",
    CONTEXTE_MODE_INVITES_DEFAUT
  );

  const contexte = normaliserContexteModeInvites(valeur);

  const mettreAJour = useCallback(
    (
      miseAJour:
        | Partial<ContexteModeInvites>
        | ((precedent: ContexteModeInvites) => Partial<ContexteModeInvites>)
    ) => {
      setValeur((precedent) => {
        const base = normaliserContexteModeInvites(precedent);
        const patch = typeof miseAJour === "function" ? miseAJour(base) : miseAJour;
        return normaliserContexteModeInvites({ ...base, ...patch });
      });
    },
    [setValeur]
  );

  const reinitialiser = useCallback(() => {
    reinitialiserStockage();
  }, [reinitialiserStockage]);

  return {
    contexte,
    mettreAJour,
    reinitialiser,
  };
}