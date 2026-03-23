// ═══════════════════════════════════════════════════════════
// Client API — Documents famille
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export interface DocumentFamille {
  id: number;
  titre: string;
  categorie: string;
  membre_famille?: string | null;
  fichier_url?: string | null;
  fichier_nom?: string | null;
  date_document?: string | null;
  date_expiration?: string | null;
  notes?: string | null;
  tags: string[];
  actif: boolean;
  est_expire: boolean;
  jours_avant_expiration?: number | null;
}

export interface CreerDocumentDTO {
  titre: string;
  categorie?: string;
  membre_famille?: string;
  date_document?: string;
  date_expiration?: string;
  notes?: string;
  tags?: string[];
}

export async function listerDocuments(
  categorie?: string,
  search?: string
): Promise<{ items: DocumentFamille[]; total: number }> {
  const params = new URLSearchParams();
  if (categorie) params.set("categorie", categorie);
  if (search) params.set("search", search);
  const { data } = await clientApi.get(`/documents?${params.toString()}`);
  return data;
}

export async function creerDocument(dto: CreerDocumentDTO): Promise<DocumentFamille> {
  const { data } = await clientApi.post("/documents", dto);
  return data;
}

export async function modifierDocument(
  id: number,
  dto: Partial<CreerDocumentDTO>
): Promise<DocumentFamille> {
  const { data } = await clientApi.patch(`/documents/${id}`, dto);
  return data;
}

export async function supprimerDocument(id: number): Promise<void> {
  await clientApi.delete(`/documents/${id}`);
}
