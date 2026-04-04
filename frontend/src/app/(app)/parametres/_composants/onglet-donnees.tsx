"use client";

import { useEffect, useState } from "react";
import { Download, Loader2, RefreshCw, Trash2, Wifi, WifiOff } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Label } from "@/composants/ui/label";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { utiliserInvalidation, utiliserMutation } from "@/crochets/utiliser-api";
import { toast } from "sonner";

export function OngletDonnees() {
  const [confirmation, setConfirmation] = useState(false);
  const [motDePasseBackup, setMotDePasseBackup] = useState("");
  const [fichierImport, setFichierImport] = useState<File | null>(null);
  const [motDePasseImport, setMotDePasseImport] = useState("");
  const [estEnLigne, setEstEnLigne] = useState(true);
  const [syncDisponible, setSyncDisponible] = useState(false);
  const [fileSyncEnAttente, setFileSyncEnAttente] = useState(0);
  const [syncEnCours, setSyncEnCours] = useState(false);
  const invalider = utiliserInvalidation();

  const backupZipMutation = utiliserMutation(
    async () => {
      const { clientApi } = await import("@/bibliotheque/api/client");
      const { data } = await clientApi.post('/api/v1/export/backup', null, {
        responseType: 'blob',
      });
      return data;
    },
    {
      onSuccess: (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `backup-matanne-${new Date().toISOString().slice(0, 10)}.zip`;
        a.click();
        URL.revokeObjectURL(url);
        toast.success("Backup téléchargé avec succès");
      },
      onError: () => toast.error("Erreur lors de l'export du backup"),
    }
  );

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    setEstEnLigne(window.navigator.onLine);

    const mettreAJourReseau = () => setEstEnLigne(window.navigator.onLine);
    const gererMessageServiceWorker = (event: MessageEvent<{ type?: string; pending?: number }>) => {
      if (event.data?.type === "SYNC_QUEUE_UPDATED" || event.data?.type === "SYNC_QUEUE_FLUSHED") {
        setFileSyncEnAttente(Number(event.data?.pending ?? 0));
        setSyncEnCours(false);
      }
    };

    window.addEventListener("online", mettreAJourReseau);
    window.addEventListener("offline", mettreAJourReseau);

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.addEventListener("message", gererMessageServiceWorker);
      navigator.serviceWorker.getRegistration().then((registration) => {
        const worker = registration?.active ?? navigator.serviceWorker.controller;
        setSyncDisponible(Boolean(worker));
        worker?.postMessage({ type: "GET_SYNC_QUEUE_STATUS" });
      }).catch(() => setSyncDisponible(false));
    }

    return () => {
      window.removeEventListener("online", mettreAJourReseau);
      window.removeEventListener("offline", mettreAJourReseau);
      if ("serviceWorker" in navigator) {
        navigator.serviceWorker.removeEventListener("message", gererMessageServiceWorker);
      }
    };
  }, []);

  const demanderEtatSync = async () => {
    if (!("serviceWorker" in navigator)) {
      toast.info("Synchronisation hors ligne indisponible sur ce navigateur");
      return;
    }
    const registration = await navigator.serviceWorker.getRegistration();
    const worker = registration?.active ?? navigator.serviceWorker.controller;
    if (!worker) {
      setSyncDisponible(false);
      toast.info("Service Worker non actif pour le moment");
      return;
    }
    setSyncDisponible(true);
    worker.postMessage({ type: "GET_SYNC_QUEUE_STATUS" });
  };

  const relancerSynchronisation = async () => {
    if (!("serviceWorker" in navigator)) {
      toast.info("Synchronisation hors ligne indisponible sur ce navigateur");
      return;
    }
    const registration = await navigator.serviceWorker.getRegistration();
    const worker = registration?.active ?? navigator.serviceWorker.controller;
    if (!worker) {
      setSyncDisponible(false);
      toast.info("Service Worker non actif pour le moment");
      return;
    }
    setSyncDisponible(true);
    setSyncEnCours(true);
    worker.postMessage({ type: "REPLAY_SYNC_QUEUE" });
    toast.success("Synchronisation relancée");
  };

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
        <div className="space-y-3 rounded-xl border bg-muted/30 p-4">
          <Label className="flex items-center gap-2">Synchronisation hors ligne</Label>
          <p className="text-sm text-muted-foreground">
            Les actions réalisées sans connexion sont stockées puis rejouées automatiquement dès le retour en ligne.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant={estEnLigne ? "default" : "destructive"}>
              {estEnLigne ? (
                <span className="inline-flex items-center gap-1"><Wifi className="h-3 w-3" /> En ligne</span>
              ) : (
                <span className="inline-flex items-center gap-1"><WifiOff className="h-3 w-3" /> Hors ligne</span>
              )}
            </Badge>
            <Badge variant="outline">{fileSyncEnAttente} action(s) en attente</Badge>
            {!syncDisponible ? <Badge variant="secondary">Service Worker indisponible</Badge> : null}
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={() => void demanderEtatSync()} disabled={!syncDisponible}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Actualiser l'état
            </Button>
            <Button
              variant="outline"
              onClick={() => void relancerSynchronisation()}
              disabled={!syncDisponible || syncEnCours || fileSyncEnAttente === 0}
            >
              {syncEnCours ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Resynchronisation...</>
              ) : (
                <><RefreshCw className="mr-2 h-4 w-4" />Relancer la synchronisation</>
              )}
            </Button>
          </div>
        </div>

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
            Télécharger mon backup complet
          </Label>
          <p className="text-sm text-muted-foreground">
            Téléchargez une archive ZIP contenant toutes vos données personnelles
            (recettes, planning, courses, inventaire, famille, etc.).
          </p>
          <Button
            variant="outline"
            onClick={() => backupZipMutation.mutate(undefined)}
            disabled={backupZipMutation.isPending}
          >
            {backupZipMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Backup en cours...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Télécharger mon backup (ZIP)
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
