// ═══════════════════════════════════════════════════════════
// Page Connexion
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { connecter } from "@/bibliotheque/api/auth";
import { utiliserStoreAuth } from "@/magasins/store-auth";
import { obtenirProfil } from "@/bibliotheque/api/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link";

const schemaConnexion = z.object({
  email: z.string().email("Email invalide"),
  mot_de_passe: z.string().min(6, "6 caractères minimum"),
});

type DonneesFormulaire = z.infer<typeof schemaConnexion>;

export default function PageConnexion() {
  const router = useRouter();
  const { definirUtilisateur } = utiliserStoreAuth();
  const [erreur, setErreur] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<DonneesFormulaire>({
    resolver: zodResolver(schemaConnexion),
  });

  async function onSubmit(donnees: DonneesFormulaire) {
    setErreur(null);
    try {
      await connecter(donnees);
      const profil = await obtenirProfil();
      definirUtilisateur(profil);
      router.push("/");
    } catch {
      setErreur("Email ou mot de passe incorrect");
    }
  }

  return (
    <Card>
      <CardHeader className="text-center">
        <div className="text-4xl mb-2">🏠</div>
        <CardTitle className="text-2xl">Assistant Matanne</CardTitle>
        <CardDescription>Connectez-vous à votre espace familial</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {erreur && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {erreur}
            </div>
          )}
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
            <Input
              id="mot_de_passe"
              type="password"
              {...register("mot_de_passe")}
            />
            {errors.mot_de_passe && (
              <p className="text-xs text-destructive">
                {errors.mot_de_passe.message}
              </p>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Connexion..." : "Se connecter"}
          </Button>
          <p className="text-sm text-muted-foreground">
            Pas encore de compte ?{" "}
            <Link href="/inscription" className="text-primary hover:underline">
              Créer un compte
            </Link>
          </p>
        </CardFooter>
      </form>
    </Card>
  );
}
