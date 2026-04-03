import { describe, expect, it } from "vitest";

import { construireDonneesTreemapInventaire } from "@/bibliotheque/inventaire-treemap";
import type { ArticleInventaire } from "@/types/inventaire";

function creerArticle(partial: Partial<ArticleInventaire>): ArticleInventaire {
  return {
    id: partial.id ?? 1,
    nom: partial.nom ?? "Article",
    quantite: partial.quantite ?? 1,
    date_ajout: partial.date_ajout ?? "2026-04-03",
    est_bas: partial.est_bas ?? false,
    est_expire: partial.est_expire ?? false,
    categorie: partial.categorie,
    unite: partial.unite,
    emplacement: partial.emplacement,
    date_peremption: partial.date_peremption,
    seuil_alerte: partial.seuil_alerte,
    nutriscore: partial.nutriscore,
    ecoscore: partial.ecoscore,
    nova_group: partial.nova_group,
  };
}

describe("construireDonneesTreemapInventaire", () => {
  it("agrege les quantites par categorie puis trie par volume", () => {
    const articles: ArticleInventaire[] = [
      creerArticle({ id: 1, nom: "Pommes", quantite: 5, categorie: "Fruits" }),
      creerArticle({ id: 2, nom: "Bananes", quantite: 3, categorie: "Fruits" }),
      creerArticle({ id: 3, nom: "Lait", quantite: 6, categorie: "Laitier" }),
    ];

    const resultat = construireDonneesTreemapInventaire(articles);

    expect(resultat).toHaveLength(2);
    expect(resultat[0].nom).toBe("Fruits");
    expect(resultat[0].quantite).toBe(8);
    expect(resultat[1].nom).toBe("Laitier");
    expect(resultat[1].quantite).toBe(6);
  });

  it("utilise 'Autre' quand la categorie est absente", () => {
    const articles: ArticleInventaire[] = [
      creerArticle({ id: 1, nom: "Mystere", quantite: 2, categorie: undefined }),
    ];

    const resultat = construireDonneesTreemapInventaire(articles);

    expect(resultat).toHaveLength(1);
    expect(resultat[0].nom).toBe("Autre");
    expect(resultat[0].quantite).toBe(2);
  });

  it("limite les sous-categories aux 8 plus grosses", () => {
    const articles: ArticleInventaire[] = Array.from({ length: 10 }).map((_, index) =>
      creerArticle({
        id: index + 1,
        nom: `Article-${index + 1}`,
        quantite: 10 - index,
        categorie: "Epicerie",
      })
    );

    const resultat = construireDonneesTreemapInventaire(articles);

    expect(resultat).toHaveLength(1);
    expect(resultat[0].sous_categories).toHaveLength(8);
    expect(resultat[0].sous_categories[0].nom).toBe("Article-1");
    expect(resultat[0].sous_categories[7].nom).toBe("Article-8");
  });
});
