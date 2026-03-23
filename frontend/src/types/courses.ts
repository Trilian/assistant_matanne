// ═══════════════════════════════════════════════════════════
// Types Courses
// ═══════════════════════════════════════════════════════════

export interface ListeCourses {
  id: number;
  nom: string;
  date_creation: string;
  est_terminee: boolean;
  articles: ArticleCourses[];
  nombre_articles: number;
  nombre_coche: number;
}

export interface ArticleCourses {
  id: number;
  nom: string;
  quantite?: number;
  unite?: string;
  categorie?: string;
  est_coche: boolean;
  prix_estime?: number;
  magasin?: string;
  ordre?: number;
}

export interface CreerArticleDTO {
  nom: string;
  quantite?: number;
  unite?: string;
  categorie?: string;
  prix_estime?: number;
  magasin?: string;
}
