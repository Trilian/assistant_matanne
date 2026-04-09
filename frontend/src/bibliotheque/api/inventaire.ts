// ═══════════════════════════════════════════════════════════
// API Inventaire
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { ObjetDonnees } from "@/types/commun";
import type { ArticleInventaire, CreerArticleInventaireDTO } from "@/types/inventaire";

/** Lister les articles de l'inventaire */
export async function listerInventaire(emplacement?: string): Promise<ArticleInventaire[]> {
  const params: Record<string, string> = {};
  if (emplacement) params.emplacement = emplacement;
  const { data } = await clientApi.get<{ items: ArticleInventaire[] } | ArticleInventaire[]>("/inventaire", { params });
  return (data as { items: ArticleInventaire[] }).items ?? (data as ArticleInventaire[]);
}

/** Lister les emplacements normalisés */
export async function listerEmplacements(): Promise<string[]> {
  const { data } = await clientApi.get<string[]>("/inventaire/emplacements");
  return data;
}

// ─── Vue consolidée Cellier ↔ Inventaire (MT-01) ───────────────────────

export interface ArticleConsolide {
  nom: string;
  nom_normalise: string;
  quantite_totale: number;
  unite: string;
  categories: string[];
  emplacements: string[];
  sources: string[];  // "cuisine" | "cellier"
  details_sources: ObjetDonnees[];
}

/** Retourne la vue unifiée des stocks cuisine + cellier (évite les doublons dans les courses) */
export async function listerInventaireConsolide(): Promise<ArticleConsolide[]> {
  const { data } = await clientApi.get<ArticleConsolide[]>("/inventaire/consolide");
  return data;
}

/** Ajouter un article à l'inventaire */
export async function ajouterArticleInventaire(
  dto: CreerArticleInventaireDTO
): Promise<ArticleInventaire> {
  const { data } = await clientApi.post<ArticleInventaire>("/inventaire", dto);
  return data;
}

/** Mettre à jour un article */
export async function modifierArticleInventaire(
  id: number,
  dto: Partial<CreerArticleInventaireDTO>
): Promise<ArticleInventaire> {
  const { data } = await clientApi.put<ArticleInventaire>(`/inventaire/${id}`, dto);
  return data;
}

/** Supprimer un article */
export async function supprimerArticleInventaire(id: number): Promise<void> {
  await clientApi.delete(`/inventaire/${id}`);
}

/** Articles en alerte (stock bas ou périmés bientôt) */
export async function obtenirAlertes(): Promise<ArticleInventaire[]> {
  const { data } = await clientApi.get<ArticleInventaire[]>("/inventaire/alertes");
  return data;
}

export interface ArticleBulk {
  nom: string;
  quantite?: number;
  categorie?: string;
  unite?: string;
}

export interface ResultatBulk {
  message: string;
}

/** Ajouter plusieurs articles en masse (depuis photo-frigo) */
export async function ajouterArticlesBulk(
  articles: ArticleBulk[],
  emplacement = "frigo"
): Promise<ResultatBulk> {
  const { data } = await clientApi.post<ResultatBulk>(
    `/inventaire/bulk?emplacement=${encodeURIComponent(emplacement)}`,
    articles
  );
  return data;
}

export interface ResultatOCRFrigo {
  articles: ArticleBulk[];
  total: number;
  crees: number;
  mis_a_jour: number;
  message?: string;
}

/** Détecte les aliments dans une photo de frigo via le endpoint unifié photo-frigo (mode preview pour checkboxes) */
export async function detecterPhotoFrigoSansImport(
  file: File,
  _emplacement = "frigo"
): Promise<ResultatOCRFrigo> {
  const fd = new FormData();
  fd.append("file", file);
  const { data } = await clientApi.post<{
    ingredients_detectes: { nom: string; quantite_estimee?: string; confiance: number }[];
  }>(`/suggestions/photo-frigo`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  const articles: ArticleBulk[] = (data.ingredients_detectes ?? []).map((ing) => ({
    nom: ing.nom,
    quantite: ing.quantite_estimee ? parseFloat(ing.quantite_estimee) || 1 : 1,
  }));
  return {
    articles,
    total: articles.length,
    crees: 0,
    mis_a_jour: 0,
    message: `${articles.length} aliment(s) détecté(s)`,
  };
}

// ─── Scan multi-codes ─────────────────────────────────────────────────

export interface ArticleBarcode {
  code: string;
  article: {
    id: number;
    nom: string;
    quantite: number;
    unite?: string;
    categorie?: string;
    emplacement?: string;
    code_barres?: string;
  };
}

export interface ResultatScanBatch {
  trouves: ArticleBarcode[];
  inconnus: string[];
}

/**
 * Résout un lot de codes-barres en articles d'inventaire.
 * Utilisé par le composant ScanneurMultiCodes.
 */
export async function scannerCodesBatch(
  codes: string[]
): Promise<ResultatScanBatch> {
  const { data } = await clientApi.post<ResultatScanBatch>(
    "/inventaire/barcode/batch",
    { codes }
  );
  return data;
}

/** Enrichir un article via OpenFoodFacts (nutriscore, ecoscore, etc.) */
export async function enrichirParCodeBarres(
  code: string
): Promise<{
  code_barres: string;
  enrichi: boolean;
  donnees?: {
    nutriscore?: string;
    ecoscore?: string;
    nova_group?: number;
    calories?: number;
    nom_produit?: string;
  };
}> {
  const { data } = await clientApi.post(`/inventaire/barcode/${code}/enrichir`);
  return data;
}
