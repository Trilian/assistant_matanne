// ═══════════════════════════════════════════════════════════
// Types Courses
// ═══════════════════════════════════════════════════════════

export interface ListeCourses {
  id: number;
  nom: string;
  etat: "brouillon" | "active" | "terminee" | string;
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
  magasin_cible?: string;
  famille_produit?: string;
  sous_famille_produit?: string;
  drive_mappe?: boolean;
  ordre?: number;
}

export interface CreerArticleDTO {
  nom: string;
  quantite?: number;
  unite?: string;
  categorie?: string;
  prix_estime?: number;
  magasin?: string;
  magasin_cible?: string;
}

export type MagasinCible = "bio_coop" | "grand_frais" | "carrefour_drive";

export const LIBELLES_MAGASINS: Record<MagasinCible, string> = {
  bio_coop: "🥬 Bio Coop",
  grand_frais: "🧀 Grand Frais",
  carrefour_drive: "🛒 Carrefour Drive",
};

export const COULEURS_MAGASINS: Record<MagasinCible, string> = {
  bio_coop: "bg-green-100 text-green-800 border-green-300",
  grand_frais: "bg-blue-100 text-blue-800 border-blue-300",
  carrefour_drive: "bg-red-100 text-red-800 border-red-300",
};

export interface CorrespondanceDrive {
  id: number;
  nom_article: string;
  ingredient_id?: number | null;
  produit_drive_id: string;
  produit_drive_nom: string;
  produit_drive_ean?: string | null;
  produit_drive_url?: string | null;
  quantite_par_defaut: number;
  nb_utilisations: number;
  actif: boolean;
}

export interface ArticleDrive {
  id: number;
  nom: string;
  ingredient_id?: number | null;
  quantite: number;
  coche: boolean;
  categorie?: string | null;
  correspondance?: CorrespondanceDrive | null;
}

export interface ArticlesParMagasin {
  liste_id: number;
  nom: string;
  magasins: Record<string, ArticleCourses[]>;
  total_articles: number;
  compteurs: Record<string, number>;
}
