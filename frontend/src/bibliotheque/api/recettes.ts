// ═══════════════════════════════════════════════════════════
// API Recettes
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { ReponsePaginee } from "@/types/api";
import type { Recette, CreerRecetteDTO, SuggestionRecette } from "@/types/recettes";

/** Lister les recettes (paginé) */
export async function listerRecettes(
  page = 1,
  taille = 20,
  recherche?: string
): Promise<ReponsePaginee<Recette>> {
  const params = new URLSearchParams({
    page: String(page),
    taille_page: String(taille),
  });
  if (recherche) params.set("recherche", recherche);
  const { data } = await clientApi.get<ReponsePaginee<Recette>>(`/recettes?${params}`);
  return data;
}

/** Obtenir une recette par ID */
export async function obtenirRecette(id: number): Promise<Recette> {
  const { data } = await clientApi.get<Recette>(`/recettes/${id}`);
  return data;
}

/** Créer une recette */
export async function creerRecette(dto: CreerRecetteDTO): Promise<Recette> {
  const { data } = await clientApi.post<Recette>("/recettes", dto);
  return data;
}

/** Mettre à jour une recette */
export async function modifierRecette(
  id: number,
  dto: Partial<CreerRecetteDTO>
): Promise<Recette> {
  const { data } = await clientApi.put<Recette>(`/recettes/${id}`, dto);
  return data;
}

/** Supprimer une recette */
export async function supprimerRecette(id: number): Promise<void> {
  await clientApi.delete(`/recettes/${id}`);
}

/** Obtenir des suggestions IA */
export async function obtenirSuggestions(contexte: string): Promise<SuggestionRecette[]> {
  const { data } = await clientApi.post<SuggestionRecette[]>("/suggestions/recettes", {
    contexte,
  });
  return data;
}

// ─── Planification "cette semaine" ───────────────────────

/** Lister les recettes planifiées pour cette semaine */
export async function listerRecettesSemaine(): Promise<Recette[]> {
  const { data } = await clientApi.get<Recette[]>("/recettes/planifiees-semaine");
  return data;
}

/** Marquer une recette "à faire cette semaine" */
export async function planifierRecetteSemaine(id: number): Promise<void> {
  await clientApi.post(`/recettes/${id}/planifier-semaine`);
}

/** Retirer une recette de "cette semaine" */
export async function deplanifierRecetteSemaine(id: number): Promise<void> {
  await clientApi.delete(`/recettes/${id}/planifier-semaine`);
}

// ─── Import de recettes ──────────────────────────────────

/** Importer une recette depuis une URL */
export async function importerRecetteURL(url: string): Promise<Recette> {
  const { data } = await clientApi.post<Recette>("/recettes/import-url", null, {
    params: { url },
  });
  return data;
}

/** Importer une recette depuis un fichier PDF */
export async function importerRecettePDF(file: File): Promise<Recette> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await clientApi.post<Recette>("/recettes/import-pdf", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

// ─── Version Jules ───────────────────────────────────────

export interface VersionJulesResult {
  nom: string;
  ingredients: string[];
  instructions: string;
  adaptations: string[];
  aliments_exclus_retires: string[];
}

/** Générer une version adaptée pour Jules (bébé/enfant) */
export async function genererVersionJules(recetteId: number): Promise<VersionJulesResult> {
  const { data } = await clientApi.post<VersionJulesResult>(`/recettes/${recetteId}/version-jules`);
  return data;
}

// ─── Génération depuis photo ─────────────────────────────

/** Générer une recette à partir d'une photo (Pixtral) */
export async function genererDepuisPhoto(file: File): Promise<Recette> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await clientApi.post<Recette>("/recettes/generer-depuis-photo", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

// ─── Recette Surprise ────────────────────────────────────

/** Obtenir une recette surprise (filtrée par saison + frigo) */
export async function obtenirRecetteSurprise(): Promise<Recette> {
  const { data } = await clientApi.get<Recette>("/recettes/surprise");
  return data;
}

export interface LienPartageRecette {
  token: string;
  url: string;
  expires_at: string;
}

/** Générer un lien de partage public temporaire pour une recette */
export async function partagerRecette(recetteId: number, dureeHeures = 48): Promise<LienPartageRecette> {
  const { data } = await clientApi.post<LienPartageRecette>(
    `/recettes/${recetteId}/partager?duree_heures=${dureeHeures}`
  );
  return data;
}

/** Exporter la recette en PDF */
export async function exporterRecettePdf(recetteId: number): Promise<void> {
  // Endpoint dédié sprint 11: /api/v1/recettes/{id}/export-pdf
  const response = await clientApi.get(`/recettes/${recetteId}/export-pdf`, {
    responseType: "blob",
  });
  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `recette_${recetteId}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

