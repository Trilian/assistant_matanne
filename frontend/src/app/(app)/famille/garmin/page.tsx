"use client";

import { useState } from "react";
import { Activity, RefreshCw, Link as LinkIcon, Unplug } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { utiliserMutation, utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { toast } from "sonner";

type StatutGarmin = {
  connected: boolean;
  display_name?: string;
  objectif_pas?: number;
  objectif_calories?: number;
};

type StatsGarmin = {
  total_pas: number;
  total_calories: number;
  total_distance_km: number;
  total_activities: number;
  streak_jours: number;
  moyenne_pas_jour: number;
  derniere_sync?: string;
  garmin_connected: boolean;
};

export default function PageGarmin() {
  const [verifier, setVerifier] = useState("");
  const invalider = utiliserInvalidation();

  const { data: statut } = utiliserRequete(["garmin", "status"], async () => {
    const { data } = await clientApi.get<StatutGarmin>("/garmin/status");
    return data;
  });

  const { data: stats } = utiliserRequete(["garmin", "stats"], async () => {
    const { data } = await clientApi.get<StatsGarmin>("/garmin/stats");
    return data;
  });

  const { mutate: connecter, isPending: enConnexion } = utiliserMutation(
    async () => {
      const { data } = await clientApi.post<{ authorization_url: string }>("/garmin/connect-url");
      return data;
    },
    {
      onSuccess: ({ authorization_url }) => {
        window.open(authorization_url, "_blank", "noopener,noreferrer");
        toast.success("Page Garmin ouverte dans un nouvel onglet");
      },
      onError: () => toast.error("Connexion Garmin indisponible"),
    }
  );

  const { mutate: finaliser, isPending: enFinalisation } = utiliserMutation(
    async () => {
      await clientApi.post("/garmin/complete", { oauth_verifier: verifier.trim() });
    },
    {
      onSuccess: () => {
        invalider(["garmin", "status"]);
        invalider(["garmin", "stats"]);
        setVerifier("");
        toast.success("Garmin connecté");
      },
      onError: () => toast.error("Impossible de finaliser la connexion Garmin"),
    }
  );

  const { mutate: synchroniser, isPending: enSync } = utiliserMutation(
    async () => {
      await clientApi.post("/garmin/sync");
    },
    {
      onSuccess: () => {
        invalider(["garmin", "stats"]);
        toast.success("Synchronisation Garmin lancée");
      },
      onError: () => toast.error("Synchronisation Garmin impossible"),
    }
  );

  const { mutate: deconnecter, isPending: enDeconnexion } = utiliserMutation(
    async () => {
      await clientApi.post("/garmin/disconnect");
    },
    {
      onSuccess: () => {
        invalider(["garmin", "status"]);
        invalider(["garmin", "stats"]);
        toast.success("Garmin déconnecté");
      },
      onError: () => toast.error("Déconnexion Garmin impossible"),
    }
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Garmin santé & sport</h1>
        <p className="text-muted-foreground">Connexion, synchronisation et statistiques d'activité.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Statut de connexion
            </CardTitle>
            <CardDescription>
              {statut?.connected ? "Garmin est connecté à votre profil." : "Garmin n'est pas encore connecté."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Utilisateur</p>
                <p className="font-medium">{statut?.display_name ?? "Profil principal"}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Objectif pas</p>
                <p className="font-medium">{statut?.objectif_pas ?? 0}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => connecter()} disabled={enConnexion}>
                <LinkIcon className="mr-2 h-4 w-4" />
                {enConnexion ? "Ouverture..." : "Connecter Garmin"}
              </Button>
              <Button variant="outline" onClick={() => synchroniser()} disabled={enSync || !statut?.connected}>
                <RefreshCw className="mr-2 h-4 w-4" />
                {enSync ? "Sync..." : "Synchroniser"}
              </Button>
              <Button variant="outline" onClick={() => deconnecter()} disabled={enDeconnexion || !statut?.connected}>
                <Unplug className="mr-2 h-4 w-4" />
                Déconnecter
              </Button>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Code de validation Garmin</p>
              <div className="flex gap-2">
                <Input value={verifier} onChange={(e) => setVerifier(e.target.value)} placeholder="Coller le oauth_verifier" />
                <Button variant="secondary" disabled={!verifier.trim() || enFinalisation} onClick={() => finaliser()}>
                  Valider
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Résumé 7 jours</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="rounded-lg border p-3">
              <p className="text-xs uppercase text-muted-foreground">Pas totaux</p>
              <p className="text-2xl font-bold">{stats?.total_pas ?? 0}</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Calories</p>
                <p className="font-semibold">{stats?.total_calories ?? 0}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Activités</p>
                <p className="font-semibold">{stats?.total_activities ?? 0}</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Distance</p>
                <p className="font-semibold">{stats?.total_distance_km?.toFixed(1) ?? "0.0"} km</p>
              </div>
              <div className="rounded-lg border p-3">
                <p className="text-xs uppercase text-muted-foreground">Streak</p>
                <p className="font-semibold">{stats?.streak_jours ?? 0} jours</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}