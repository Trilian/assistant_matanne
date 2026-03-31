"use client";

import { useState } from "react";
import { Download, Loader2, Trash2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserInvalidation, utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { toast } from "sonner";

export function OngletDonnees() {
  const [confirmation, setConfirmation] = useState(false);
  const [motDePasseBackup, setMotDePasseBackup] = useState("");
  const [fichierImport, setFichierImport] = useState<File | null>(null);
  const [motDePasseImport, setMotDePasseImport] = useState("");
  const [texteConfirmation, setTexteConfirmation] = useState("");
  const [motifSuppression, setMotifSuppression] = useState("");
  const [suppressionOuverte, setSuppressionOuverte] = useState(false);
  const invalider = utiliserInvalidation();

  const { data: resume, isLoading: chargementResume } = utiliserRequete(
    ["rgpd", "resume"],
    async () => {
      const { obtenirResumeDonnees } = await import("@/bibliotheque/api/rgpd");
      return obtenirResumeDonnees();
    }
  );

  const exportMutation = utiliserMutation(
    async () => {
      const { exporterDonnees } = await import("@/bibliotheque/api/rgpd");
      return exporterDonnees();
    },
    {
      onSuccess: (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `mes-donnees-${new Date().toISOString().slice(0, 10)}.zip`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success("Export téléchargé avec succès");
      },
      onError: () => toast.error("Erreur lors de l'export des données"),
    }
  );

  const suppressionMutation = utiliserMutation(
    async () => {
      const { supprimerCompte } = await import("@/bibliotheque/api/rgpd");
      return supprimerCompte(texteConfirmation, motifSuppression || undefined);
    },
    {
      onSuccess: () => {
        toast.success("Compte supprimé. Déconnexion...");
        setTimeout(() => {
          window.location.href = "/connexion";
        }, 2000);
      },
      onError: () => toast.error("Erreur lors de la suppression du compte"),
    }
  );

  const viderCache = () => {
    invalider([]);
    setConfirmation(true);
    setTimeout(() => setConfirmation(false), 2000);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Données</CardTitle>
        <CardDescription>Gestion du cache et des données</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Cache local</Label>
          <p className="text-sm text-muted-foreground">
            Videz le cache pour recharger toutes les données depuis le serveur.
          </p>
          <Button variant="outline" onClick={viderCache}>
            {confirmation ? (
              <>Cache vidé !</>
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                Vider le cache
              </>
            )}
          </Button>
        </div>

        <div className="space-y-2">
          <Label>Stockage navigateur</Label>
          <p className="text-sm text-muted-foreground">
            Taille estimée des données stockées localement.
          </p>
          <Badge variant="secondary">
            {typeof window !== "undefined"
              ? `${(JSON.stringify(localStorage).length / 1024).toFixed(1)} KB`
              : "—"}
          </Badge>
        </div>

        <div className="border-t pt-6 space-y-3">
          <Label className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Backup données (JSON)
          </Label>
          <p className="text-sm text-muted-foreground">
            Exportez toutes vos données en JSON. Ajoutez un mot de passe pour chiffrer le fichier (AES-256).
          </p>
          <div className="flex items-center gap-2">
            <Input
              type="password"
              placeholder="Mot de passe (optionnel)"
              value={motDePasseBackup}
              onChange={(e) => setMotDePasseBackup(e.target.value)}
              className="max-w-xs"
            />
          </div>
          <Button
            variant="outline"
            onClick={async () => {
              const { telechargerBackupJson, DOMAINES_DEFAUT } = await import(
                "@/bibliotheque/api/export"
              );
              try {
                await telechargerBackupJson(
                  [...DOMAINES_DEFAUT],
                  motDePasseBackup || undefined
                );
                toast.success(
                  motDePasseBackup ? "Backup chiffré téléchargé" : "Backup téléchargé"
                );
              } catch {
                toast.error("Erreur lors du téléchargement du backup");
              }
            }}
          >
            <Download className="mr-2 h-4 w-4" />
            {motDePasseBackup ? "Télécharger (.json.enc)" : "Télécharger (.json)"}
          </Button>
          <div className="space-y-2 pt-2">
            <Label>Restaurer depuis un backup</Label>
            <Input
              type="file"
              accept=".json,.json.enc"
              onChange={(e) => setFichierImport(e.target.files?.[0] ?? null)}
            />
            {fichierImport?.name.endsWith(".enc") && (
              <Input
                type="password"
                placeholder="Mot de passe du fichier chiffré"
                value={motDePasseImport}
                onChange={(e) => setMotDePasseImport(e.target.value)}
              />
            )}
            {fichierImport && (
              <Button
                variant="outline"
                onClick={async () => {
                  const { restaurerDepuisJson } = await import(
                    "@/bibliotheque/api/export"
                  );
                  try {
                    await restaurerDepuisJson(fichierImport, {
                      motDePasse: motDePasseImport || undefined,
                    });
                    toast.success("Données restaurées avec succès");
                    setFichierImport(null);
                    setMotDePasseImport("");
                  } catch {
                    toast.error("Erreur lors de la restauration");
                  }
                }}
              >
                Restaurer
              </Button>
            )}
          </div>
        </div>

        <div className="border-t pt-6 space-y-2">
          <Label className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export de vos données (RGPD)
          </Label>
          <p className="text-sm text-muted-foreground">
            Téléchargez une archive ZIP contenant toutes vos données personnelles.
          </p>
          {resume && !chargementResume && (
            <p className="text-xs text-muted-foreground">
              {resume.total_elements} éléments répartis sur {resume.categories.length} catégories
            </p>
          )}
          <Button
            variant="outline"
            onClick={() => exportMutation.mutate(undefined)}
            disabled={exportMutation.isPending}
          >
            {exportMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Export en cours...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Télécharger mes données
              </>
            )}
          </Button>
        </div>

        <div className="border-t pt-6 space-y-4">
          <Label className="flex items-center gap-2 text-destructive">
            <Trash2 className="h-4 w-4" />
            Supprimer mon compte
          </Label>
          <p className="text-sm text-muted-foreground">
            Cette action est irréversible. Toutes vos données seront définitivement supprimées.
          </p>
          {!suppressionOuverte ? (
            <Button
              variant="destructive"
              onClick={() => setSuppressionOuverte(true)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Supprimer mon compte
            </Button>
          ) : (
            <div className="space-y-3 rounded-lg border border-destructive/50 p-4">
              <div className="space-y-2">
                <Label>Motif (optionnel)</Label>
                <Input
                  value={motifSuppression}
                  onChange={(e) => setMotifSuppression(e.target.value)}
                  placeholder="Pourquoi souhaitez-vous supprimer votre compte ?"
                />
              </div>
              <div className="space-y-2">
                <Label>
                  Tapez <strong>SUPPRIMER MON COMPTE</strong> pour confirmer
                </Label>
                <Input
                  value={texteConfirmation}
                  onChange={(e) => setTexteConfirmation(e.target.value)}
                  placeholder="SUPPRIMER MON COMPTE"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="destructive"
                  disabled={
                    texteConfirmation !== "SUPPRIMER MON COMPTE" ||
                    suppressionMutation.isPending
                  }
                  onClick={() => suppressionMutation.mutate(undefined)}
                >
                  {suppressionMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Suppression...
                    </>
                  ) : (
                    "Confirmer la suppression"
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSuppressionOuverte(false);
                    setTexteConfirmation("");
                    setMotifSuppression("");
                  }}
                >
                  Annuler
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
