// ═══════════════════════════════════════════════════════════
// API Preferences — Paramètres utilisateur
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export interface Preferences {
  user_id: string;
  nb_adultes: number;
  jules_present: boolean;
  jules_age_mois: number | null;
  temps_semaine: number;
  temps_weekend: number;
  aliments_exclus: string[];
  aliments_favoris: string[];
  poisson_par_semaine: number;
  vegetarien_par_semaine: number;
  viande_rouge_max: number;
  robots: string[];
  magasins_preferes: string[];
}

/** Récupérer les préférences */
export async function obtenirPreferences(): Promise<Preferences> {
  const { data } = await clientApi.get<Preferences>("/preferences");
  return data;
}

/** Créer ou remplacer les préférences (PUT) */
export async function sauvegarderPreferences(
  prefs: Omit<Preferences, "user_id">
): Promise<Preferences> {
  const { data } = await clientApi.put<Preferences>("/preferences", prefs);
  return data;
}

/** Mise à jour partielle des préférences (PATCH) */
export async function modifierPreferences(
  prefs: Partial<Omit<Preferences, "user_id">>
): Promise<Preferences> {
  const { data } = await clientApi.patch<Preferences>("/preferences", prefs);
  return data;
}
