// ═══════════════════════════════════════════════════════════
// API Batch Cooking
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  SessionBatchCooking,
  CreerSessionBatchDTO,
} from "@/types/batch-cooking";

/** Lister les sessions de batch cooking */
export async function listerSessionsBatch(
  page = 1,
  pageSize = 20,
  statut?: string
): Promise<{ items: SessionBatchCooking[]; total: number; pages: number }> {
  const params: Record<string, string | number> = { page, page_size: pageSize };
  if (statut) params.statut = statut;
  const { data } = await clientApi.get("/batch-cooking", { params });
  return data;
}

/** Obtenir une session avec ses étapes */
export async function obtenirSessionBatch(
  id: number
): Promise<SessionBatchCooking> {
  const { data } = await clientApi.get<SessionBatchCooking>(
    `/batch-cooking/${id}`
  );
  return data;
}

/** Créer une nouvelle session */
export async function creerSessionBatch(
  dto: CreerSessionBatchDTO
): Promise<SessionBatchCooking> {
  const { data } = await clientApi.post<SessionBatchCooking>(
    "/batch-cooking",
    dto
  );
  return data;
}

/** Supprimer une session */
export async function supprimerSessionBatch(id: number): Promise<void> {
  await clientApi.delete(`/batch-cooking/${id}`);
}

export interface GenererSessionDepuisPlanningOptions {
  planning_id: number;
  date_session: string;
  nom?: string;
  avec_jules?: boolean;
}

export interface GenererSessionDepuisPlanningResult {
  session_id: number;
  nom: string;
  nb_recettes: number;
  recettes: { id: number; nom: string; portions: number }[];
  duree_estimee: number;
  robots_utilises: string[];
}

/** Générer une session batch depuis un planning */
export async function genererSessionDepuisPlanning(
  options: GenererSessionDepuisPlanningOptions
): Promise<GenererSessionDepuisPlanningResult> {
  const { data } = await clientApi.post<GenererSessionDepuisPlanningResult>(
    "/batch-cooking/generer-depuis-planning",
    options
  );
  return data;
}

export interface PreparationBatch {
  id: number;
  nom: string;
  portions_initiales?: number;
  portions_restantes?: number;
  date_preparation?: string;
  date_peremption?: string;
  localisation?: string;
  container?: string;
  consomme: boolean;
  jours_avant_peremption?: number | null;
  alerte_peremption?: boolean;
}

/** Lister les préparations en stock (congélateur/frigo) */
export async function listerPreparations(
  consomme?: boolean
): Promise<{ items: PreparationBatch[] }> {
  const params: Record<string, string> = {};
  if (consomme !== undefined) params.consomme = String(consomme);
  const { data } = await clientApi.get<{ items: PreparationBatch[] }>(
    "/batch-cooking/preparations",
    { params }
  );
  return data;
}
