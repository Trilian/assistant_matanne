// ═══════════════════════════════════════════════════════════
// Types Inventaire
// ═══════════════════════════════════════════════════════════

export interface ArticleInventaire {
  id: number;
  nom: string;
  quantite: number;
  unite?: string;
  categorie?: string;
  emplacement?: string;
  date_peremption?: string;
  date_ajout: string;
  seuil_alerte?: number;
  est_bas: boolean;
  est_expire: boolean;
  // OpenFoodFacts enrichment (populated when code_barres is present)
  nutriscore?: string;
  ecoscore?: string;
  nova_group?: number;
}

export interface CreerArticleInventaireDTO {
  nom: string;
  quantite: number;
  unite?: string;
  categorie?: string;
  emplacement?: string;
  date_peremption?: string;
  seuil_alerte?: number;
}
