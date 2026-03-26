// ═══════════════════════════════════════════════════════════
// API Inventaire
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";
import type { ArticleInventaire, CreerArticleInventaireDTO } from "@/types/inventaire";

/** Lister les articles de l'inventaire */
export async function listerInventaire(): Promise<ArticleInventaire[]> {
  const { data } = await clientApi.get<ArticleInventaire[]>("/inventaire");
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

/** Analyse une photo de frigo via IA et importe les aliments dans l'inventaire */
export async function ocrPhotoFrigo(
  file: File,
  emplacement = "frigo"
): Promise<ResultatOCRFrigo> {
  const fd = new FormData();
  fd.append("photo", file);
  const { data } = await clientApi.post<ResultatOCRFrigo>(
    `/inventaire/ocr-photo-frigo?emplacement=${encodeURIComponent(emplacement)}`,
    fd,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return data;
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
