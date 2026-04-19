import { z } from "zod";

/** Schémas jeux */
export const schemaPariSportif = z.object({
  match_id: z.coerce.number().int().min(1, "Match requis"),
  prediction: z.string().min(1, "Prédiction requise"),
  cote: z.coerce.number().min(1, "Cote requise"),
  type_pari: z.string().default("1N2"),
  mise: z.coerce.number().min(0).default(0),
  est_virtuel: z.boolean().default(true),
  notes: z.string().nullish(),
});

export type DonneesPariSportif = z.infer<typeof schemaPariSportif>;

/** Grille Loto (5 numéros 1-49, 1 numéro chance 1-10) */
export const schemaGrilleLoto = z.object({
  numeros: z
    .array(z.coerce.number().int().min(1).max(49))
    .length(5, "5 numéros requis"),
  numero_chance: z.coerce.number().int().min(1).max(10),
  est_fleche: z.boolean().default(false),
  notes: z.string().nullish(),
});

export type DonneesGrilleLoto = z.infer<typeof schemaGrilleLoto>;

/** Grille EuroMillions (5 numéros 1-50, 2 étoiles 1-12) */
export const schemaGrilleEuromillions = z.object({
  numeros: z
    .array(z.coerce.number().int().min(1).max(50))
    .length(5, "5 numéros requis"),
  etoiles: z
    .array(z.coerce.number().int().min(1).max(12))
    .length(2, "2 étoiles requises"),
  est_etoile_plus: z.boolean().default(false),
  notes: z.string().nullish(),
});

export type DonneesGrilleEuromillions = z.infer<typeof schemaGrilleEuromillions>;
