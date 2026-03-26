// ═══════════════════════════════════════════════════════════
// Barre de progression — Indicateur de chargement navigation (Idée B)
// ═══════════════════════════════════════════════════════════

"use client";

import { AppProgressBar as ProgressBar } from "next-nprogress-bar";

/**
 * Barre de progression fine en haut de page lors des navigations.
 * S'affiche automatiquement à chaque changement de route.
 */
export function BarreProgression() {
  return (
    <ProgressBar
      height="3px"
      color="hsl(var(--primary))"
      options={{ showSpinner: false }}
      shallowRouting
    />
  );
}
