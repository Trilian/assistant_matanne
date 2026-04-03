import type { ArticleInventaire } from "@/types/inventaire";

export interface NoeudTreemapInventaire {
  nom: string;
  quantite: number;
  sous_categories: Array<{ nom: string; quantite: number }>;
}

export function construireDonneesTreemapInventaire(
  articles: ArticleInventaire[]
): NoeudTreemapInventaire[] {
  const parCategorie = articles.reduce(
    (acc, article) => {
      const categorie = article.categorie || "Autre";
      if (!acc[categorie]) {
        acc[categorie] = {
          nom: categorie,
          quantite: 0,
          sous_categories: [],
        };
      }

      const quantite = Number(article.quantite ?? 0);
      acc[categorie].quantite += quantite;
      acc[categorie].sous_categories.push({
        nom: article.nom,
        quantite,
      });

      return acc;
    },
    {} as Record<string, NoeudTreemapInventaire>
  );

  return Object.values(parCategorie)
    .map((categorie) => ({
      ...categorie,
      sous_categories: categorie.sous_categories
        .sort((a, b) => b.quantite - a.quantite)
        .slice(0, 8),
    }))
    .sort((a, b) => b.quantite - a.quantite);
}
