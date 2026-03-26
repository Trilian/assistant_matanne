// ═══════════════════════════════════════════════════════════
// API Anti-Gaspillage
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { DonneesAntiGaspillage, HistoriqueGaspillage } from "@/types/anti-gaspillage";

/** Obtenir le score anti-gaspillage, articles urgents et recettes rescue */
export async function obtenirAntiGaspillage(
  jours = 7
): Promise<DonneesAntiGaspillage> {
  const { data } = await clientApi.get<DonneesAntiGaspillage>(
    "/anti-gaspillage",
    { params: { jours } }
  );
  return data;
}

/** Obtenir l'historique et badges de gamification (4 dernières semaines par défaut) */
export async function obtenirHistoriqueGaspillage(
  semaines = 4
): Promise<HistoriqueGaspillage> {
  const { data } = await clientApi.get<HistoriqueGaspillage>(
    "/anti-gaspillage/historique",
    { params: { semaines } }
  );
  return data;
}
