export type EtatFraicheurSync = "fresh" | "warning" | "stale";

export function evaluerFraicheurSync(dateIso: string): EtatFraicheurSync {
  const deltaMs = Date.now() - new Date(dateIso).getTime();
  const heures = deltaMs / (1000 * 60 * 60);
  if (heures > 24) {
    return "stale";
  }
  if (heures >= 12) {
    return "warning";
  }
  return "fresh";
}

export function libelleFraicheurSync(etat: EtatFraicheurSync): string {
  if (etat === "stale") {
    return "A rafraichir (>24h)";
  }
  if (etat === "warning") {
    return "A surveiller (12-24h)";
  }
  return "A jour (<12h)";
}
