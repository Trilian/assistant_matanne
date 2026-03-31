"use client";

import { useState } from "react";
import { Loader2, Save } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserInvalidation, utiliserMutation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { toast } from "sonner";

export interface UtilisateurParametres {
  id?: string;
  email?: string;
  nom?: string;
  role?: string;
}

interface OngletProfilProps {
  utilisateur: UtilisateurParametres | null;
}

export function OngletProfil({ utilisateur }: OngletProfilProps) {
  const [nom, setNom] = useState(utilisateur?.nom ?? "");
  const [email] = useState(utilisateur?.email ?? "");
  const invalider = utiliserInvalidation();

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    () => clientApi.put("/auth/me", { nom }),
    {
      onSuccess: () => {
        invalider(["auth", "profil"]);
        toast.success("Profil sauvegardé");
      },
      onError: () => toast.error("Erreur lors de la sauvegarde"),
    }
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profil</CardTitle>
        <CardDescription>Gérez vos informations personnelles</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4 max-w-md">
        <div className="space-y-2">
          <Label htmlFor="profil-nom">Nom</Label>
          <Input
            id="profil-nom"
            value={nom}
            onChange={(e) => setNom(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="profil-email">Email</Label>
          <Input id="profil-email" value={email} disabled />
          <p className="text-xs text-muted-foreground">
            L&apos;email ne peut pas être modifié
          </p>
        </div>
        <div className="space-y-2">
          <Label>Rôle</Label>
          <div>
            <Badge variant="secondary">{utilisateur?.role ?? "—"}</Badge>
          </div>
        </div>
        <Button
          onClick={() => sauvegarder(undefined)}
          disabled={isPending || nom === utilisateur?.nom}
        >
          {isPending ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Save className="mr-2 h-4 w-4" />
          )}
          Enregistrer
        </Button>
      </CardContent>
    </Card>
  );
}
