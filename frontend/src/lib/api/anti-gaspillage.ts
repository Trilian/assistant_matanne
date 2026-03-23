// ═══════════════════════════════════════════════════════════
// API Anti-Gaspillage
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { DonneesAntiGaspillage } from "@/types/anti-gaspillage";

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
