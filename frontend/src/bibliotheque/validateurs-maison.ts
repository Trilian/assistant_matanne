import { z } from "zod";

/** Schémas maison */
export const schemaProjetMaison = z.object({
  nom: z.string().min(1, "Nom requis").max(200),
  description: z.string().nullish(),
  statut: z.string().max(50).default("planifié"),
  priorite: z.string().max(50).nullish(),
  date_debut: z.string().nullish(),
  date_fin_prevue: z.string().nullish(),
});

export const schemaTacheEntretien = z.object({
  nom: z.string().min(1, "Nom requis").max(200),
  description: z.string().nullish(),
  categorie: z.string().max(100).nullish(),
  piece: z.string().max(100).nullish(),
  frequence_jours: z.coerce.number().int().min(1).nullish(),
  duree_minutes: z.coerce.number().int().min(1).nullish(),
  responsable: z.string().max(100).nullish(),
  priorite: z.string().max(50).nullish(),
});

export type DonneesProjetMaison = z.infer<typeof schemaProjetMaison>;
export type DonneesTacheEntretien = z.infer<typeof schemaTacheEntretien>;
