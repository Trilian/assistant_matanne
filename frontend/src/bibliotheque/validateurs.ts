// ═══════════════════════════════════════════════════════════
// Validateurs Zod — Miroir des schemas Pydantic backend
// ═══════════════════════════════════════════════════════════

import { z } from "zod";

/** Schema connexion */
export const schemaConnexion = z.object({
  email: z.string().email("Email invalide"),
  mot_de_passe: z.string().min(6, "6 caractères minimum"),
});

/** Schema inscription */
export const schemaInscription = z
  .object({
    nom: z.string().min(2, "2 caractères minimum"),
    email: z.string().email("Email invalide"),
    mot_de_passe: z.string().min(6, "6 caractères minimum"),
    confirmation: z.string(),
  })
  .refine((d) => d.mot_de_passe === d.confirmation, {
    message: "Les mots de passe ne correspondent pas",
    path: ["confirmation"],
  });

/** Schema création recette */
export const schemaRecette = z.object({
  nom: z.string().min(2, "Nom requis"),
  description: z.string().optional(),
  instructions: z.string().optional(),
  temps_preparation: z.coerce.number().min(0).optional(),
  temps_cuisson: z.coerce.number().min(0).optional(),
  portions: z.coerce.number().min(1).optional(),
  difficulte: z.enum(["facile", "moyen", "difficile"]).optional(),
  categorie: z.string().optional(),
  ingredients: z
    .array(
      z.object({
        nom: z.string().min(1, "Nom requis"),
        quantite: z.coerce.number().min(0).optional(),
        unite: z.string().optional(),
      })
    )
    .min(1, "Au moins un ingrédient"),
});

/** Schema article courses */
export const schemaArticleCourses = z.object({
  nom: z.string().min(1, "Nom requis"),
  quantite: z.coerce.number().min(0).optional(),
  unite: z.string().optional(),
  categorie: z.string().optional(),
  prix_estime: z.coerce.number().min(0).optional(),
});

/** Schema article inventaire */
export const schemaArticleInventaire = z.object({
  nom: z.string().min(1, "Nom requis"),
  quantite: z.coerce.number().min(0, "Quantité requise"),
  unite: z.string().optional(),
  categorie: z.string().optional(),
  emplacement: z.string().optional(),
  date_peremption: z.string().optional(),
  seuil_alerte: z.coerce.number().min(0).optional(),
});

export type DonneesConnexion = z.infer<typeof schemaConnexion>;
export type DonneesInscription = z.infer<typeof schemaInscription>;
export type DonneesRecette = z.infer<typeof schemaRecette>;
export type DonneesArticleCourses = z.infer<typeof schemaArticleCourses>;
export type DonneesArticleInventaire = z.infer<typeof schemaArticleInventaire>;
