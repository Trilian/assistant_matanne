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
