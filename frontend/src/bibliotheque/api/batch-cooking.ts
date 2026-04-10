// ═══════════════════════════════════════════════════════════
// API Batch Cooking
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  SessionBatchCooking,
  CreerSessionBatchDTO,
} from "@/types/batch-cooking";
import type {
  PreparationBatch,
  ConfigBatchCooking,
  GenererSessionDepuisPlanningOptions,
  GenererSessionDepuisPlanningResult,
  ModifierSessionBatchDTO,
} from "@/types/batch-cooking"

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

/** Consommer des portions d'une préparation */
export async function consommerPreparation(
  id: number,
  portions = 1
): Promise<{ id: number; nom: string; portions_restantes: number; consomme: boolean }> {
  const { data } = await clientApi.post(`/batch-cooking/preparations/${id}/consommer`, null, {
    params: { portions },
  });
  return data;
}

/** Modifier une session (PATCH partiel) */
export async function modifierSessionBatch(
  id: number,
  dto: ModifierSessionBatchDTO
): Promise<SessionBatchCooking> {
  const { data } = await clientApi.patch<SessionBatchCooking>(`/batch-cooking/${id}`, dto)
  return data
}

/** Obtenir la configuration batch cooking de l'utilisateur */
export async function obtenirConfigBatch(): Promise<ConfigBatchCooking> {
  const { data } = await clientApi.get<ConfigBatchCooking>("/batch-cooking/config")
  return data
}

/** Générer les étapes IA pour une session existante et les persister */
export async function genererEtapesSession(
  id: number
): Promise<SessionBatchCooking> {
  const { data } = await clientApi.post<SessionBatchCooking>(
    `/batch-cooking/${id}/generer-etapes`
  )
  return data
}
