// ═══════════════════════════════════════════════════════════
// Page Connexion (avec support 2FA)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { connecter, login2FA, obtenirProfil } from "@/bibliotheque/api/auth";
import { utiliserStoreAuth } from "@/magasins/store-auth";
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
import { Eye, EyeOff, ShieldCheck } from "lucide-react";

const schemaConnexion = z.object({
  email: z.string().email("Email invalide"),
  mot_de_passe: z.string().min(6, "6 caractères minimum"),
});

type DonneesFormulaire = z.infer<typeof schemaConnexion>;

export default function PageConnexion() {
  const router = useRouter();
  const { definirUtilisateur } = utiliserStoreAuth();
  const [erreur, setErreur] = useState<string | null>(null);
  const [montrerMdp, setMontrerMdp] = useState(false);
  const [etape2FA, setEtape2FA] = useState(false);
  const [tempToken, setTempToken] = useState("");
  const [code2FA, setCode2FA] = useState("");
  const [enVerification, setEnVerification] = useState(false);

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
      const reponse = await connecter(donnees);

      if (reponse.requires_2fa && reponse.temp_token) {
        setTempToken(reponse.temp_token);
        setEtape2FA(true);
        return;
      }

      const profil = await obtenirProfil();
      definirUtilisateur(profil);
      router.push("/");
    } catch {
      setErreur("Email ou mot de passe incorrect");
    }
  }

  async function onVerifier2FA() {
    setErreur(null);
    setEnVerification(true);
    try {
      await login2FA(tempToken, code2FA);
      const profil = await obtenirProfil();
      definirUtilisateur(profil);
      router.push("/");
    } catch {
      setErreur("Code 2FA invalide");
    } finally {
      setEnVerification(false);
    }
  }

  // ─── Étape 2FA ───
  if (etape2FA) {
    return (
      <Card>
        <CardHeader className="text-center">
          <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <ShieldCheck className="h-6 w-6 text-primary" />
          </div>
          <CardTitle className="text-2xl">Vérification 2FA</CardTitle>
          <CardDescription>
            Entrez le code à 6 chiffres de votre application d&apos;authentification
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {erreur && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {erreur}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="code-2fa">Code de vérification</Label>
            <Input
              id="code-2fa"
              type="text"
              inputMode="numeric"
              placeholder="000000"
              maxLength={8}
              value={code2FA}
              onChange={(e) => setCode2FA(e.target.value.replace(/\D/g, ""))}
              autoFocus
              className="text-center text-2xl tracking-widest"
            />
            <p className="text-xs text-muted-foreground">
              Vous pouvez aussi utiliser un code de récupération
            </p>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          <Button
            className="w-full"
            disabled={code2FA.length < 6 || enVerification}
            onClick={onVerifier2FA}
          >
            {enVerification ? "Vérification..." : "Vérifier"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => { setEtape2FA(false); setCode2FA(""); setErreur(null); }}
          >
            Retour à la connexion
          </Button>
        </CardFooter>
      </Card>
    );
  }

  // ─── Formulaire login classique ───
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
                {montrerMdp ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
              </button>
            </div>
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
