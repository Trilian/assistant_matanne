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

// ═══════════════════════════════════════════════════════════
// Famille
// ═══════════════════════════════════════════════════════════

/** Schema création anniversaire */
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

/** Schema création événement familial */
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

/** Schema création activité famille */
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

/** Schema création dépense budget famille */
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

// ═══════════════════════════════════════════════════════════
// Maison
// ═══════════════════════════════════════════════════════════

/** Schema création projet maison */
export const schemaProjetMaison = z.object({
  nom: z.string().min(1, "Nom requis").max(200),
  description: z.string().nullish(),
  statut: z.string().max(50).default("planifié"),
  priorite: z.string().max(50).nullish(),
  date_debut: z.string().nullish(),
  date_fin_prevue: z.string().nullish(),
});

/** Schema création tâche entretien */
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

// ═══════════════════════════════════════════════════════════
// Jeux
// ═══════════════════════════════════════════════════════════

/** Schema création pari sportif */
export const schemaPariSportif = z.object({
  match_id: z.coerce.number().int().min(1, "Match requis"),
  prediction: z.string().min(1, "Prédiction requise"),
  cote: z.coerce.number().min(1, "Cote requise"),
  type_pari: z.string().default("1N2"),
  mise: z.coerce.number().min(0).default(0),
  est_virtuel: z.boolean().default(true),
  notes: z.string().nullish(),
});

// ═══════════════════════════════════════════════════════════
// Utilitaires
// ═══════════════════════════════════════════════════════════

/** Schema création note */
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

/** Schema création entrée journal */
export const schemaJournal = z.object({
  date_entree: z.string().min(1, "Date requise"),
  contenu: z.string().min(1, "Contenu requis"),
  humeur: z.string().nullish(),
  energie: z.coerce.number().int().min(1).max(10).nullish(),
  gratitudes: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

/** Schema création contact */
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

export type DonneesAnniversaire = z.infer<typeof schemaAnniversaire>;
export type DonneesEvenementFamilial = z.infer<typeof schemaEvenementFamilial>;
export type DonneesActiviteFamille = z.infer<typeof schemaActiviteFamille>;
export type DonneesDepenseBudget = z.infer<typeof schemaDepenseBudget>;
export type DonneesProjetMaison = z.infer<typeof schemaProjetMaison>;
export type DonneesTacheEntretien = z.infer<typeof schemaTacheEntretien>;
export type DonneesPariSportif = z.infer<typeof schemaPariSportif>;
export type DonneesNote = z.infer<typeof schemaNote>;
export type DonneesJournal = z.infer<typeof schemaJournal>;
export type DonneesContact = z.infer<typeof schemaContact>;
