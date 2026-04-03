// ═══════════════════════════════════════════════════════════
// API Planning
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  PlanningSemaine,
  PlanningMensuel,
  RapportConflitsPlanning,
  RepasPlanning,
  CreerRepasPlanningDTO,
  SuggestionRecettePlanning,
  GenererPlanningParams,
} from "@/types/planning";
import { exporterPdf } from "@/bibliotheque/api/export";

/** Obtenir le planning de la semaine courante ou spécifiée */
export async function obtenirPlanningSemaine(dateDebut?: string): Promise<PlanningSemaine> {
  const params = dateDebut ? `?date_debut=${dateDebut}` : "";
  const { data } = await clientApi.get<PlanningSemaine>(`/planning/semaine${params}`);
  return data;
}

/** Obtenir le planning mensuel */
export async function obtenirPlanningMensuel(mois: string): Promise<PlanningMensuel> {
  const { data } = await clientApi.get<PlanningMensuel>(`/planning/mensuel?mois=${encodeURIComponent(mois)}`);
  return data;
}

/** Obtenir les conflits de la semaine */
export async function obtenirConflitsPlanning(dateDebut?: string): Promise<RapportConflitsPlanning> {
  const params = dateDebut ? `?date_debut=${encodeURIComponent(dateDebut)}` : "";
  const { data } = await clientApi.get<RapportConflitsPlanning>(`/planning/conflits${params}`);
  return data;
}

/** Ajouter/modifier un repas dans le planning */
export async function definirRepas(dto: CreerRepasPlanningDTO): Promise<RepasPlanning> {
  const { data } = await clientApi.post<RepasPlanning>("/planning/repas", dto);
  return data;
}

/** Supprimer un repas du planning */
export async function supprimerRepas(id: number): Promise<void> {
  await clientApi.delete(`/planning/repas/${id}`);
}

/** Valider un planning (proposé → actif) */
export async function validerPlanning(planningId: number): Promise<{ message: string; id: number }> {
  const { data } = await clientApi.post<{ message: string; id: number }>(
    `/planning/${planningId}/valider`
  );
  return data;
}

/** Adapter tous les repas du planning pour Jules */
export async function adapterPlanningJules(
  planningId: number
): Promise<{ message: string; id: number; data?: { nb_adapte?: number; nb_erreurs?: number } }> {
  const { data } = await clientApi.post<{
    message: string;
    id: number;
    data?: { nb_adapte?: number; nb_erreurs?: number };
  }>(`/planning/${planningId}/adapter-jules`);
  return data;
}

/** Marquer un repas comme consommé (décrémenter l'inventaire) */
export async function marquerRepasConsomme(
  repasId: number,
  portions = 1
): Promise<{ message: string; id: number }> {
  const { data } = await clientApi.post<{ message: string; id: number }>(
    `/planning/repas/${repasId}/consomme`,
    null,
    { params: { portions } }
  );
  return data;
}

/** Obtenir des alternatives pour un repas */
export async function obtenirAlternativesRepas(
  repasId: number,
  nombre = 5
): Promise<{ alternatives: unknown[]; repas_id: number }> {
  const { data } = await clientApi.get(`/planning/repas/${repasId}/alternatives`, {
    params: { nombre },
  });
  return data;
}

/** Générer un planning IA pour la semaine */
export async function genererPlanningSemaine(
  params?: GenererPlanningParams
): Promise<PlanningSemaine> {
  const { data } = await clientApi.post<PlanningSemaine>("/planning/generer", params ?? {});
  return data;
}

/** Obtenir des suggestions rapides de recettes pour un créneau */
export async function obtenirSuggestionsRapides(
  typeRepas = "diner",
  nombre = 6
): Promise<SuggestionRecettePlanning[]> {
  const { data } = await clientApi.get<{ suggestions: SuggestionRecettePlanning[] }>(
    `/planning/suggestions-rapides?type_repas=${typeRepas}&nombre=${nombre}`
  );
  return data.suggestions;
}

/** Exporter le planning en iCalendar (.ics) et déclencher le téléchargement */
export async function exporterPlanningIcal(semaines = 2): Promise<void> {
  const response = await clientApi.get(`/planning/export/ical?semaines=${semaines}`, {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const a = document.createElement("a");
  a.href = url;
  a.download = "planning-repas.ics";
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

/** Exporter le planning en PDF */
export async function exporterPlanningPdf(planningId?: number): Promise<void> {
  if (!planningId) {
    throw new Error("planning_id requis pour l'export PDF du planning");
  }
  await exporterPdf("planning", planningId);
}

// ─── Nutrition hebdomadaire ─────────────────────────────────

export interface NutritionJour {
  calories: number;
  proteines: number;
  lipides: number;
  glucides: number;
  repas: { id: number; type: string; nom_recette: string | null; calories: number | null }[];
}

export interface NutritionHebdo {
  semaine_debut: string;
  semaine_fin: string;
  totaux: { calories: number; proteines: number; lipides: number; glucides: number };
  moyenne_calories_par_jour: number;
  par_jour: Record<string, NutritionJour>;
  nb_repas_sans_donnees: number;
  nb_repas_total: number;
}

/** Obtenir l'analyse nutritionnelle d'une semaine */
export async function obtenirNutritionHebdo(semaine?: string): Promise<NutritionHebdo> {
  const params = semaine ? `?semaine=${semaine}` : "";
  const { data } = await clientApi.get<NutritionHebdo>(`/planning/nutrition-hebdo${params}`);
  return data;
}

// ─── Semaine unifiée trans-modules (AC1) ─────────────────────

export interface SemaineUnifiee {
  meta: { semaine_debut: string; semaine_fin: string };
  repas: Record<string, { id: number; type: string; recette_id: number | null; nom_recette: string | null }[]>;
  activites_famille: { id: number; date: string | null; titre: string; type: string | null }[];
  taches_maison: { nom: string; categorie: string | null; duree_estimee_min: number | null }[];
}

/** Vue unifiée de la semaine (repas + activités famille + matchs + tâches maison) */
export async function obtenirSemaineUnifiee(dateDebut?: string): Promise<SemaineUnifiee> {
  const params = dateDebut ? `?date_debut=${dateDebut}` : "";
  const { data } = await clientApi.get<SemaineUnifiee>(`/planning/semaine-unifiee${params}`);
  return data;
}

// ─── Stubs tablette ────────────────────────────────────────

/** Planning du jour — extrait de la semaine courante */
export async function obtenirPlanningAujourdhui(): Promise<PlanningSemaine> {
  return obtenirPlanningSemaine();
}

/** Météo courante (stub — à connecter à un service météo) */
export async function obtenirMeteo(): Promise<{ temperature: number; condition: string; humidity?: number } | null> {
  return null;
}

