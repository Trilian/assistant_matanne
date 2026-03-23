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
