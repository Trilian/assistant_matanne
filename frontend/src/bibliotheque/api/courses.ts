// ═══════════════════════════════════════════════════════════
// API Courses
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type {
  ListeCourses,
  ArticleCourses,
  CreerArticleDTO,
  ArticlesParMagasin,
  ArticleDrive,
  CorrespondanceDrive,
} from "@/types/courses";

type ListeCoursesResumeApi = {
  id: number;
  nom: string;
  etat?: string;
  items_count?: number;
  created_at?: string;
};

type ListeCoursesDetailApi = {
  id: number;
  nom: string;
  etat?: string;
  archivee?: boolean;
  created_at?: string;
  items: Array<{
    id: number;
    nom: string;
    quantite?: number;
    coche?: boolean;
    categorie?: string;
    magasin_cible?: string;
    prix_estime?: number;
  }>;
};

/** Lister toutes les listes de courses */
export async function listerListesCourses(): Promise<ListeCourses[]> {
  const { data } = await clientApi.get<{
    items: ListeCoursesResumeApi[];
  }>("/courses");

  return (data.items ?? []).map((liste) => ({
    id: liste.id,
    nom: liste.nom,
    etat: liste.etat ?? "brouillon",
    date_creation: liste.created_at ?? new Date().toISOString(),
    est_terminee: (liste.etat ?? "") === "terminee",
    articles: [],
    nombre_articles: liste.items_count ?? 0,
    nombre_coche: 0,
  }));
}

/** Obtenir une liste par ID */
export async function obtenirListeCourses(id: number): Promise<ListeCourses> {
  const { data } = await clientApi.get<ListeCoursesDetailApi>(`/courses/${id}`);

  const articles = (data.items ?? []).map((item) => ({
    id: item.id,
    nom: item.nom,
    quantite: item.quantite,
    categorie: item.categorie,
    est_coche: Boolean(item.coche),
    magasin_cible: item.magasin_cible,
    prix_estime: item.prix_estime,
  }));

  return {
    id: data.id,
    nom: data.nom,
    etat: data.etat ?? "brouillon",
    date_creation: data.created_at ?? new Date().toISOString(),
    est_terminee: (data.etat ?? "") === "terminee",
    articles,
    nombre_articles: articles.length,
    nombre_coche: articles.filter((article) => article.est_coche).length,
  };
}

/** Créer une nouvelle liste */
export async function creerListeCourses(nom: string): Promise<ListeCourses> {
  const { data } = await clientApi.post<{ id: number }>("/courses", { nom });
  return obtenirListeCourses(data.id);
}

/** Ajouter un article à une liste */
export async function ajouterArticle(
  listeId: number,
  article: CreerArticleDTO
): Promise<ArticleCourses> {
  const { data } = await clientApi.post<{ id: number }>(
    `/courses/${listeId}/items`,
    article
  );
  const detail = await obtenirListeCourses(listeId);
  const cree = detail.articles.find((item) => item.id === data.id);
  if (!cree) {
    throw new Error("Article créé introuvable dans la liste");
  }
  return cree;
}

/** Cocher/décocher un article */
export async function cocherArticle(
  listeId: number,
  articleId: number,
  estCoche: boolean
): Promise<ArticleCourses> {
  const detail = await obtenirListeCourses(listeId);
  const courant = detail.articles.find((item) => item.id === articleId);
  if (!courant) {
    throw new Error("Article introuvable");
  }

  await clientApi.put(`/courses/${listeId}/items/${articleId}`, {
    nom: courant.nom,
    quantite: courant.quantite ?? 1,
    unite: courant.unite,
    categorie: courant.categorie,
    coche: estCoche,
    prix_estime: courant.prix_estime,
  });

  return {
    ...courant,
    est_coche: estCoche,
  };
}

/** Supprimer un article */
export async function supprimerArticle(
  listeId: number,
  articleId: number
): Promise<void> {
  await clientApi.delete(`/courses/${listeId}/items/${articleId}`);
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

// ─── Validation & Intelligence ────────────────────────────

/** Valider une liste (incrémenter inventaire + historique achats) */
export async function validerCourses(listeId: number): Promise<{ message: string; id: number }> {
  const { data } = await clientApi.post<{ message: string; id: number }>(
    `/courses/${listeId}/valider`
  );
  return data;
}

/** Confirmer une liste brouillon (brouillon -> active) */
export async function confirmerCourses(listeId: number): Promise<{ message: string; id: number }> {
  const { data } = await clientApi.post<{ message: string; id: number }>(
    `/courses/${listeId}/confirmer`
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
export interface HistoriquePrixCoursesItem {
  article_nom: string;
  categorie: string | null;
  rayon_magasin: string | null;
  derniere_achat: string | null;
  prix_dernier: number | null;
  prix_moyen: number | null;
  variation: number | null;
  nb_achats: number;
}

export async function obtenirHistoriquePrixCourses(): Promise<{
  items: HistoriquePrixCoursesItem[];
  total: number;
}> {
  const { data } = await clientApi.get("/courses/historique-prix");
  return data;
}

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

// ─── Multi-magasins ───────────────────────────────────────

/** Récupérer les articles d'une liste groupés par magasin */
export async function obtenirArticlesParMagasin(
  listeId: number,
  magasin?: string
): Promise<ArticlesParMagasin> {
  const params = magasin ? `?magasin=${encodeURIComponent(magasin)}` : "";
  const { data } = await clientApi.get<ArticlesParMagasin>(
    `/courses/${listeId}/par-magasin${params}`
  );
  return data;
}

/** Récupérer les articles Carrefour Drive enrichis avec correspondances */
export async function obtenirArticlesDrive(
  listeId: number
): Promise<ArticleDrive[]> {
  const { data } = await clientApi.get<ArticleDrive[]>(
    `/courses/${listeId}/articles-drive`
  );
  return data;
}

// ─── Correspondances Carrefour Drive ──────────────────────

/** Lister les correspondances article → produit Carrefour Drive */
export async function listerCorrespondancesDrive(
  actifOnly = true
): Promise<CorrespondanceDrive[]> {
  const { data } = await clientApi.get<CorrespondanceDrive[]>(
    `/courses/correspondances-drive`,
    { params: { actif_only: actifOnly } }
  );
  return data;
}

/** Créer ou mettre à jour une correspondance Drive (upsert) */
export async function creerCorrespondanceDrive(
  payload: Omit<CorrespondanceDrive, "id" | "nb_utilisations" | "actif">
): Promise<CorrespondanceDrive> {
  const { data } = await clientApi.post<CorrespondanceDrive>(
    `/courses/correspondances-drive`,
    payload
  );
  return data;
}

/** Désactiver une correspondance Drive */
export async function supprimerCorrespondanceDrive(
  correspondanceId: number
): Promise<void> {
  await clientApi.delete(`/courses/correspondances-drive/${correspondanceId}`);
}

/** Mettre à jour le magasin cible d'un article */
export async function modifierMagasinArticle(
  listeId: number,
  articleId: number,
  magasinCible: string | null
): Promise<ArticleCourses> {
  const detail = await obtenirListeCourses(listeId);
  const courant = detail.articles.find((item) => item.id === articleId);
  if (!courant) throw new Error("Article introuvable");

  await clientApi.put(`/courses/${listeId}/items/${articleId}`, {
    nom: courant.nom,
    quantite: courant.quantite ?? 1,
    unite: courant.unite,
    categorie: courant.categorie,
    coche: courant.est_coche,
    magasin_cible: magasinCible,
  });

  return { ...courant, magasin_cible: magasinCible ?? undefined };
}
