import { z } from "zod";

/** Schémas d'authentification */
export const schemaConnexion = z.object({
  email: z.string().email("Email invalide"),
  mot_de_passe: z.string().min(6, "6 caractères minimum"),
});

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

export type DonneesConnexion = z.infer<typeof schemaConnexion>;
export type DonneesInscription = z.infer<typeof schemaInscription>;
