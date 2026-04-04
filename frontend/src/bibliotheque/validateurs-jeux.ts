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
