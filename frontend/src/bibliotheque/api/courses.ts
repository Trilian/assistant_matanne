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
  options?: { soustraireStock?: boolean; nomListe?: string }
): Promise<GenererCoursesResult> {
  const { data } = await clientApi.post<GenererCoursesResult>(
    "/courses/generer-depuis-planning",
    {
      semaine_debut: semaineDebut,
      soustraire_stock: options?.soustraireStock ?? true,
      nom_liste: options?.nomListe ?? "Courses de la semaine",
    }
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
