// ═══════════════════════════════════════════════════════════
// API Telegram — Intégration Phase 5.2
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

/**
 * Envoyer le planning de la semaine via Telegram avec boutons interactifs
 * Appelé après genererPlanningSemaine() pour notifier les utilisateurs via Telegram
 * 
 * Le callback_data sera formaté comme:
 * - planning_valider:ID (valide le planning)
 * - planning_modifier:ID (lien web pour modifier)
 * - planning_regenerer:ID (régénère un nouveau planning)
 */
export async function envoyerPlanningTelegram(
  planningId: number,
  planningTexte?: string
): Promise<{ message: string; id?: number | null }> {
  const { data } = await clientApi.post<{ message: string; id?: number | null }>(
    "/telegram/envoyer-planning",
    {
      planning_id: planningId,
      contenu: planningTexte || undefined,
    }
  );
  return data;
}

/**
 * Envoyer la liste de courses via Telegram avec boutons interactifs
 * Appelé après confirmerCourses() pour notifier les utilisateurs via Telegram
 * 
 * Le callback_data sera formaté comme:
 * - courses_confirmer:ID (confirme la liste)
 * - courses_ajouter:ID (lien web pour ajouter des articles)
 * - courses_refaire:ID (crée une nouvelle liste)
 */
export async function envoyerListeCoursesTelegram(
  listeId: number,
  nomListe?: string
): Promise<{ message: string; id?: number | null }> {
  const { data } = await clientApi.post<{ message: string; id?: number | null }>(
    "/telegram/envoyer-courses",
    {
      liste_id: listeId,
      nom_liste: nomListe || undefined,
    }
  );
  return data;
}
