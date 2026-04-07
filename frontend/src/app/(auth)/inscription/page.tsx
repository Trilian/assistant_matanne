// ═══════════════════════════════════════════════════════════
// Page Inscription
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { inscrire } from "@/bibliotheque/api/auth";
import { utiliserStoreAuth } from "@/magasins/store-auth";
import { obtenirProfil } from "@/bibliotheque/api/auth";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import Link from "next/link";
import { Eye, EyeOff } from "lucide-react";

const schemaInscription = z
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

type DonneesFormulaire = z.infer<typeof schemaInscription>;

export default function PageInscription() {
  const router = useRouter();
  const { definirUtilisateur } = utiliserStoreAuth();
  const [erreur, setErreur] = useState<string | null>(null);
  const [montrerMdp, setMontrerMdp] = useState(false);
  const [montrerConfirmation, setMontrerConfirmation] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<DonneesFormulaire>({
    resolver: zodResolver(schemaInscription),
  });

  async function onSubmit(donnees: DonneesFormulaire) {
    setErreur(null);
    try {
      await inscrire({
        nom: donnees.nom,
        email: donnees.email,
        mot_de_passe: donnees.mot_de_passe,
      });
      const profil = await obtenirProfil();
      definirUtilisateur(profil);
      router.push("/");
    } catch {
      setErreur("Impossible de créer le compte. Réessayez.");
    }
  }

  return (
    <Card>
      <CardHeader className="text-center">
        <div className="text-4xl mb-2">🏠</div>
        <CardTitle className="text-2xl">Créer un compte</CardTitle>
        <CardDescription>Rejoignez votre espace familial</CardDescription>
      </CardHeader>
      <form method="post" onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {erreur && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {erreur}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="nom">Nom</Label>
            <Input id="nom" placeholder="Votre nom" {...register("nom")} />
            {errors.nom && (
              <p className="text-xs text-destructive">{errors.nom.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="famille@example.com"
              {...register("email")}
            />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="mot_de_passe">Mot de passe</Label>
            <div className="relative">
              <Input
                id="mot_de_passe"
                type={montrerMdp ? "text" : "password"}
                className="pr-10"
                {...register("mot_de_passe")}
              />
              <button
                type="button"
                onClick={() => setMontrerMdp((v) => !v)}
                className="absolute inset-y-0 right-0 flex items-center px-3 text-muted-foreground hover:text-foreground"
                aria-label={montrerMdp ? "Masquer le mot de passe" : "Afficher le mot de passe"}
              >
                {montrerMdp ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.mot_de_passe && (
              <p className="text-xs text-destructive">
                {errors.mot_de_passe.message}
              </p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirmation">Confirmer le mot de passe</Label>
            <div className="relative">
              <Input
                id="confirmation"
                type={montrerConfirmation ? "text" : "password"}
                className="pr-10"
                {...register("confirmation")}
              />
              <button
                type="button"
                onClick={() => setMontrerConfirmation((v) => !v)}
                className="absolute inset-y-0 right-0 flex items-center px-3 text-muted-foreground hover:text-foreground"
                aria-label={montrerConfirmation ? "Masquer le mot de passe" : "Afficher le mot de passe"}
              >
                {montrerConfirmation ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.confirmation && (
              <p className="text-xs text-destructive">
                {errors.confirmation.message}
              </p>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Création..." : "Créer le compte"}
          </Button>
          <p className="text-sm text-muted-foreground">
            Déjà un compte ?{" "}
            <Link href="/connexion" className="text-primary hover:underline">
              Se connecter
            </Link>
          </p>
        </CardFooter>
      </form>
    </Card>
  );
}
