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
  nb_poisson_blanc: number;
  nb_poisson_gras: number;
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

// ─── Préférences canaux de notification (canaux notification) ─────────────────────

export interface CanauxParCategorie {
  rappels: string[];
  alertes: string[];
  resumes: string[];
}

export interface PreferencesNotifications {
  user_id: string | null;
  courses_rappel: boolean;
  repas_suggestion: boolean;
  stock_alerte: boolean;
  meteo_alerte: boolean;
  budget_alerte: boolean;
  canal_prefere: string;
  canaux_par_categorie: CanauxParCategorie;
  notifications_par_module: Record<string, boolean>;
  quiet_hours_start: string;
  quiet_hours_end: string;
  mode_vacances: boolean;
  checklist_voyage_auto: boolean;
}

/** Récupérer les préférences de notification */
export async function obtenirPreferencesNotifications(): Promise<PreferencesNotifications> {
  const { data } = await clientApi.get<PreferencesNotifications>("/preferences/notifications");
  return data;
}

/** Mettre à jour les préférences de notification (upsert) */
export async function sauvegarderPreferencesNotifications(
  prefs: Partial<Omit<PreferencesNotifications, "user_id">>
): Promise<PreferencesNotifications> {
  const { data } = await clientApi.put<PreferencesNotifications>("/preferences/notifications", prefs);
  return data;
}
