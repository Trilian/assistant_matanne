import { z } from "zod";

/** Schémas famille */
export const schemaAnniversaire = z.object({
  nom_personne: z.string().min(1, "Nom requis").max(200),
  date_naissance: z.string().min(1, "Date requise"),
  relation: z.enum([
    "parent",
    "enfant",
    "grand_parent",
    "oncle_tante",
    "cousin",
    "ami",
    "collegue",
  ]),
  rappel_jours_avant: z.array(z.number().int()).default([7, 1, 0]),
  idees_cadeaux: z.string().nullish(),
  notes: z.string().nullish(),
});

export const schemaEvenementFamilial = z.object({
  titre: z.string().min(1, "Titre requis").max(200),
  date_evenement: z.string().min(1, "Date requise"),
  type_evenement: z.enum([
    "anniversaire",
    "fete",
    "vacances",
    "rentree",
    "tradition",
  ]),
  recurrence: z.enum(["annuelle", "mensuelle", "unique"]).default("unique"),
  rappel_jours_avant: z.coerce.number().int().default(7),
  notes: z.string().nullish(),
  participants: z.array(z.string()).nullish(),
});

export const schemaActiviteFamille = z.object({
  titre: z.string().min(1, "Titre requis"),
  date_prevue: z.string().min(1, "Date requise"),
  description: z.string().nullish(),
  type_activite: z.string().default("sortie"),
  duree_heures: z.coerce.number().min(0).nullish(),
  lieu: z.string().nullish(),
  qui_participe: z.array(z.string()).nullish(),
  cout_estime: z.coerce.number().min(0).nullish(),
  statut: z.string().default("planifié"),
  notes: z.string().nullish(),
});

export const schemaDepenseBudget = z.object({
  categorie: z.string().min(1, "Catégorie requise"),
  montant: z.coerce.number().min(0.01, "Montant requis"),
  date: z.string().optional(),
  description: z.string().nullish(),
  magasin: z.string().nullish(),
  est_recurrent: z.boolean().default(false),
  frequence_recurrence: z.string().nullish(),
  notes: z.string().nullish(),
});

export type DonneesAnniversaire = z.infer<typeof schemaAnniversaire>;
export type DonneesEvenementFamilial = z.infer<typeof schemaEvenementFamilial>;
export type DonneesActiviteFamille = z.infer<typeof schemaActiviteFamille>;
export type DonneesDepenseBudget = z.infer<typeof schemaDepenseBudget>;
