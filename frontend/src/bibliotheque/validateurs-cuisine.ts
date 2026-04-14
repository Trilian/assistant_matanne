import { z } from "zod";

/** Schémas cuisine : recettes, courses, inventaire */
export const schemaRecette = z.object({
  nom: z.string().min(2, "Nom requis"),
  description: z.string().optional(),
  instructions: z.string().optional(),
  temps_preparation: z.coerce.number().min(0).optional(),
  temps_cuisson: z.coerce.number().min(0).optional(),
  portions: z.coerce.number().min(1).optional(),
  difficulte: z.enum(["facile", "moyen", "difficile"]).optional(),
  categorie: z.string().min(1, "Catégorie requise"),  compatible_cookeo: z.boolean().optional(),
  compatible_monsieur_cuisine: z.boolean().optional(),
  compatible_airfryer: z.boolean().optional(),
  instructions_cookeo: z.string().optional(),
  instructions_monsieur_cuisine: z.string().optional(),
  instructions_airfryer: z.string().optional(),  ingredients: z
    .array(
      z.object({
        nom: z.string().min(1, "Nom requis"),
        quantite: z.coerce.number().min(0).optional(),
        unite: z.string().optional(),
      })
    )
    .min(1, "Au moins un ingrédient"),
});

export const schemaArticleCourses = z.object({
  nom: z.string().min(1, "Nom requis"),
  quantite: z.coerce.number().min(0).optional(),
  unite: z.string().optional(),
  categorie: z.string().optional(),
  prix_estime: z.coerce.number().min(0).optional(),
  magasin_cible: z.string().optional(),
});

export const schemaArticleInventaire = z.object({
  nom: z.string().min(1, "Nom requis"),
  quantite: z.coerce.number().min(0, "Quantité requise"),
  unite: z.string().optional(),
  categorie: z.string().optional(),
  emplacement: z.string().optional(),
  date_peremption: z.string().optional(),
  seuil_alerte: z.coerce.number().min(0).optional(),
});

export type DonneesRecette = z.infer<typeof schemaRecette>;
export type DonneesArticleCourses = z.infer<typeof schemaArticleCourses>;
export type DonneesArticleInventaire = z.infer<typeof schemaArticleInventaire>;
