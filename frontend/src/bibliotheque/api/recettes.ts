// ═══════════════════════════════════════════════════════════
// API Recettes
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { ReponsePaginee } from "@/types/api";
import type { Recette, CreerRecetteDTO, DoublonRecette, SuggestionRecette } from "@/types/recettes";
import { construireCalendrierStatique } from "@/bibliotheque/saison-fallback";

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

/** Ajouter aux favoris */
export async function ajouterAuFavori(id: number): Promise<void> {
  await clientApi.post(`/recettes/${id}/favori`);
}

/** Retirer des favoris */
export async function retirerDuFavori(id: number): Promise<void> {
  await clientApi.delete(`/recettes/${id}/favori`);
}

/** Obtenir des suggestions IA */
export async function obtenirSuggestions(contexte: string): Promise<SuggestionRecette[]> {
  const { data } = await clientApi.get<{ suggestions: SuggestionRecette[] }>("/suggestions/recettes", {
    params: { contexte },
  });
  return data.suggestions ?? [];
}

// ─── Planification "cette semaine" ───────────────────────

/** Recettes saisonnières — ingrédients de saison */
export interface RecetteSaisonniere extends Recette {
  nb_ingredients_saison: number;
  nb_ingredients_total: number;
  score_saison: number;
}

export interface ReponseSaisonnieres {
  items: RecetteSaisonniere[];
  total: number;
  page: number;
  page_size: number;
  pages_totales: number;
  mois: number;
  produits_saison: string[];
}

/** Lister les recettes de saison */
export async function listerRecettesSaisonnieres(
  page = 1,
  mois = 0
): Promise<ReponseSaisonnieres> {
  const { data } = await clientApi.get<ReponseSaisonnieres>("/recettes/saisonnieres", {
    params: { page, mois },
  });
  return data;
}

/** Calendrier saisonnier — données par mois */
export interface IngredientSaisonCalendrier {
  nom: string;
  categorie: string;
  bio_local: boolean;
}

export interface MoisCalendrier {
  mois: number;
  nom: string;
  ingredients: IngredientSaisonCalendrier[];
}

export interface PaireSaisonCalendrier {
  ingredients: string[];
  description: string;
  saison: string;
}

export interface ReponseCalendrierSaisonnier {
  mois_courant: number;
  saison_courante: string;
  calendrier: MoisCalendrier[];
  paires_saison: PaireSaisonCalendrier[];
}

/** Récupérer le calendrier saisonnier complet (fallback statique si le backend est inaccessible) */
export async function obtenirCalendrierSaisonnier(): Promise<ReponseCalendrierSaisonnier> {
  try {
    const { data } = await clientApi.get<ReponseCalendrierSaisonnier>("/recettes/calendrier-saisonnier");
    return data;
  } catch {
    // Données purement statiques — on peut les servir hors-ligne sans perte de valeur
    return construireCalendrierStatique();
  }
}

export interface ReponseDoublonsRecettes {
  items: DoublonRecette[];
  total: number;
  seuil: number;
}

/** Lister les recettes planifiées pour cette semaine */
export async function listerRecettesSemaine(): Promise<Recette[]> {
  const { data } = await clientApi.get<Recette[]>("/recettes/planifiees-semaine");
  return data;
}

/** Détecter les recettes potentiellement en doublon dans la collection */
export async function obtenirDoublonsRecettes(seuil = 0.72): Promise<ReponseDoublonsRecettes> {
  const { data } = await clientApi.get<ReponseDoublonsRecettes>("/recettes/doublons", {
    params: { seuil },
  });
  return data;
}

/** Fusionner deux recettes similaires — conserve id_a_garder, supprime id_a_supprimer */
export async function fusionnerRecettes(
  idAGarder: number,
  idASupprimer: number,
  nouveauNom?: string
): Promise<Recette> {
  const { data } = await clientApi.post<Recette>("/recettes/fusionner", {
    id_a_garder: idAGarder,
    id_a_supprimer: idASupprimer,
    ...(nouveauNom ? { nouveau_nom: nouveauNom } : {}),
  });
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

/** Importer plusieurs recettes depuis une liste d'URLs */
export async function importerRecettesLot(urls: string[]): Promise<{
  total: number;
  importees: number;
  echouees: number;
  resultats: Array<{ url: string; succes: boolean; recette_id?: number; nom?: string; erreur?: string }>;
}> {
  const { data } = await clientApi.post("/recettes/import-lot", null, {
    params: { urls },
    paramsSerializer: { indexes: null },
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
  id: number;
  recette_base_id: number;
  type_version: string;
  recette_nom: string | null;
  instructions_modifiees: string | null;
  ingredients_modifies: Record<string, string> | null;
  notes_bebe: string | null;
  modifications_resume: string[];
  alertes: string[];
  age_mois_jules: number | null;
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

/** Exporter la recette en PDF */
export async function exporterRecettePdf(recetteId: number): Promise<void> {
  // Endpoint dédié dédié: /api/v1/recettes/{id}/export-pdf
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

/** Générer via l'IA les étapes de préparation d'une recette sans instructions */
export async function enrichirInstructionsRecette(recetteId: number): Promise<{ enrichies: number; recette_id: number }> {
  const { data } = await clientApi.post<{ enrichies: number; recette_id: number }>(
    `/recettes/${recetteId}/enrichir-instructions`
  );
  return data;
}

