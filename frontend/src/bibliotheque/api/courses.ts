// ═══════════════════════════════════════════════════════════
// API Courses
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { ListeCourses, ArticleCourses, CreerArticleDTO } from "@/types/courses";

/** Lister toutes les listes de courses */
export async function listerListesCourses(): Promise<ListeCourses[]> {
  const { data } = await clientApi.get<ListeCourses[]>("/courses");
  return data;
}

/** Obtenir une liste par ID */
export async function obtenirListeCourses(id: number): Promise<ListeCourses> {
  const { data } = await clientApi.get<ListeCourses>(`/courses/${id}`);
  return data;
}

/** Créer une nouvelle liste */
export async function creerListeCourses(nom: string): Promise<ListeCourses> {
  const { data } = await clientApi.post<ListeCourses>("/courses", { nom });
  return data;
}

/** Ajouter un article à une liste */
export async function ajouterArticle(
  listeId: number,
  article: CreerArticleDTO
): Promise<ArticleCourses> {
  const { data } = await clientApi.post<ArticleCourses>(
    `/courses/${listeId}/articles`,
    article
  );
  return data;
}

/** Cocher/décocher un article */
export async function cocherArticle(
  listeId: number,
  articleId: number,
  estCoche: boolean
): Promise<ArticleCourses> {
  const { data } = await clientApi.patch<ArticleCourses>(
    `/courses/${listeId}/articles/${articleId}`,
    { est_coche: estCoche }
  );
  return data;
}

/** Supprimer un article */
export async function supprimerArticle(
  listeId: number,
  articleId: number
): Promise<void> {
  await clientApi.delete(`/courses/${listeId}/articles/${articleId}`);
}

/** Résultat de la génération de courses depuis planning */
export interface GenererCoursesResult {
  liste_id: number;
  nom: string;
  total_articles: number;
  articles_en_stock: number;
  contexte?: {
    nb_invites: number;
    evenements: string[];
    multiplicateur_quantites: number;
  };
  articles: Array<{
    nom: string;
    quantite: number;
    unite: string;
    rayon: string;
    en_stock: number;
  }>;
  par_rayon: Record<string, number>;
}

/** Générer une liste de courses depuis le planning de la semaine */
export async function genererCoursesDepuisPlanning(
  semaineDebut: string,
  options?: {
    soustraireStock?: boolean;
    nomListe?: string;
    nbInvites?: number;
    evenements?: string[];
  }
): Promise<GenererCoursesResult> {
  const { data } = await clientApi.post<GenererCoursesResult>(
    "/courses/generer-depuis-planning",
    {
      semaine_debut: semaineDebut,
      soustraire_stock: options?.soustraireStock ?? true,
      nom_liste: options?.nomListe ?? "Courses de la semaine",
      nb_invites: options?.nbInvites ?? 0,
      evenements: options?.evenements ?? [],
    }
  );
  return data;
}

export interface PredictionCoursesItem {
  article_nom: string;
  categorie: string | null;
  rayon_magasin: string | null;
  frequence_jours: number;
  jours_depuis_dernier_achat: number;
  retard_jours: number;
  confiance: number;
  confiance_contextualisee: number;
  ingredient_id: number | null;
  quantite_suggeree: number;
  unite_suggeree: string;
  contexte_applique: {
    nb_invites: number;
    evenements: string[];
    raisons: string[];
  };
}

export interface PredictionsCoursesResponse {
  items: PredictionCoursesItem[];
  total: number;
  meta: {
    source: string;
    scoring: string;
    contexte: {
      nb_invites: number;
      evenements: string[];
    };
  };
}

export async function obtenirPredictionsCourses(params?: {
  limite?: number;
  inclureDejaSurListe?: boolean;
  nbInvites?: number;
  evenements?: string[];
}): Promise<PredictionsCoursesResponse> {
  const searchParams = new URLSearchParams();
  searchParams.set("limite", String(params?.limite ?? 8));
  if (params?.inclureDejaSurListe) {
    searchParams.set("inclure_deja_sur_liste", "true");
  }
  if ((params?.nbInvites ?? 0) > 0) {
    searchParams.set("nb_invites", String(params?.nbInvites));
  }
  for (const evenement of params?.evenements ?? []) {
    searchParams.append("evenements", evenement);
  }

  const { data } = await clientApi.get<PredictionsCoursesResponse>(
    `/courses/predictions?${searchParams.toString()}`
  );
  return data;
}

// ─── OCR Ticket de caisse ─────────────────────────────────

export interface ArticleImporteOCR {
  nom: string;
  quantite: number;
  article_id: number;
}

export interface ArticleOCRBrut {
  description: string;
  quantite: number;
  prix_unitaire: number | null;
  prix_total: number;
}

export interface ResultatOCRTicket {
  success: boolean;
  message: string;
  donnees_ocr: {
    magasin: string | null;
    date: string | null;
    articles: ArticleOCRBrut[];
    sous_total: number | null;
    tva: number | null;
    total: number | null;
    mode_paiement: string | null;
  } | null;
  articles_importes: ArticleImporteOCR[];
  articles_non_importes: ArticleOCRBrut[];
  liste_id: number | null;
}

/**
 * Analyse un ticket de caisse par OCR.
 * Si `listeId` est fourni, importe les articles dans la liste.
 */
export async function analyserTicketCaisse(
  file: File,
  listeId?: number
): Promise<ResultatOCRTicket> {
  const formData = new FormData();
  formData.append("file", file);
  const params = listeId != null ? `?liste_id=${listeId}` : "";
  const { data } = await clientApi.post<ResultatOCRTicket>(
    `/courses/ocr-ticket-caisse${params}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
}

// ─── Validation & Intelligence ────────────────────────────

/** Valider une liste (incrémenter inventaire + historique achats) */
export async function validerCourses(listeId: number): Promise<{ message: string; id: number }> {
  const { data } = await clientApi.post<{ message: string; id: number }>(
    `/courses/${listeId}/valider`
  );
  return data;
}

/** Suggestions bio/local pour la liste */
export interface SuggestionBioLocal {
  article_id: number;
  nom: string;
  en_saison: boolean;
  bio_disponible: boolean;
  local_disponible: boolean;
  producteur: string | null;
  alternative_bio: string | null;
}

export async function obtenirSuggestionsBioLocal(
  listeId: number
): Promise<{ liste_id: number; mois: string; suggestions: SuggestionBioLocal[]; nb_en_saison: number }> {
  const { data } = await clientApi.get(`/courses/${listeId}/bio-local`);
  return data;
}

/** Articles récurrents suggérés (basé sur l'historique d'achats) */
export interface ArticleRecurrent {
  article_nom: string;
  categorie: string | null;
  frequence_jours: number;
  jours_depuis_dernier_achat: number;
  retard_jours: number;
  nb_achats_total: number;
}

export async function obtenirRecurrentsSuggeres(): Promise<{
  suggestions: ArticleRecurrent[];
  total: number;
}> {
  const { data } = await clientApi.get("/courses/recurrents-suggeres");
  return data;
}

export interface OptimisationBudgetCourses {
  liste_id: number;
  nom_liste: string;
  budget_cible: number;
  estimation_totale: number;
  economie_potentielle: number;
  niveau_alerte: "ok" | "attention" | "critique";
  substitutions: Array<{
    ingredient_original: string;
    suggestion: string;
    raison: string;
    economie_estimee?: number | null;
  }>;
  priorites: Array<{
    nom: string;
    rayon: string;
    quantite: number;
    cout_estime: number;
    indispensable: boolean;
  }>;
  message: string;
}

/** Optimiser une liste de courses selon un budget cible (IA + heuristiques). */
export async function optimiserBudgetCoursesIA(
  budgetCible?: number
): Promise<OptimisationBudgetCourses> {
  const params = budgetCible != null ? `?budget_cible=${budgetCible}` : "";
  const { data } = await clientApi.get<OptimisationBudgetCourses>(
    `/courses/optimiser-budget-ia${params}`
  );
  return data;
}

/** Récupérer un QR PNG de partage de liste */
export async function obtenirQrPartageListe(
  listeId: number,
  options?: { includeChecked?: boolean }
): Promise<Blob> {
  const { data } = await clientApi.get(`/courses/${listeId}/share-qr`, {
    params: { include_checked: options?.includeChecked ?? false },
    responseType: "blob",
  });
  return data as Blob;
}
