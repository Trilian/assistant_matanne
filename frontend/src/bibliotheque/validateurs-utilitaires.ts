import { z } from "zod";

/** Schémas utilitaires */
export const schemaNote = z.object({
  titre: z.string().min(1, "Titre requis").max(200),
  contenu: z.string().nullish(),
  categorie: z.string().default("general"),
  couleur: z.string().nullish(),
  epingle: z.boolean().default(false),
  est_checklist: z.boolean().default(false),
  items_checklist: z.array(z.record(z.string(), z.unknown())).nullish(),
  tags: z.array(z.string()).default([]),
});

export const schemaJournal = z.object({
  date_entree: z.string().min(1, "Date requise"),
  contenu: z.string().min(1, "Contenu requis"),
  humeur: z.string().nullish(),
  energie: z.coerce.number().int().min(1).max(10).nullish(),
  gratitudes: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

export const schemaContact = z.object({
  nom: z.string().min(1, "Nom requis").max(200),
  categorie: z.string().default("autre"),
  specialite: z.string().nullish(),
  telephone: z.string().nullish(),
  email: z.string().email("Email invalide").nullish(),
  adresse: z.string().nullish(),
  horaires: z.string().nullish(),
  favori: z.boolean().default(false),
});

export type DonneesNote = z.infer<typeof schemaNote>;
export type DonneesJournal = z.infer<typeof schemaJournal>;
export type DonneesContact = z.infer<typeof schemaContact>;
