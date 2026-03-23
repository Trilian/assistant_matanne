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
