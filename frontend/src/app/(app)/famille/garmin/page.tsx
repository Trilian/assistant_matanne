"use client";

import { useState } from "react";
import { Activity, RefreshCw, Link as LinkIcon, Unplug, Sparkles, CloudSun } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { SkeletonPage } from "@/composants/ui/skeleton-page";
import { EtatVide } from "@/composants/ui/etat-vide";
import { utiliserMutation, utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { obtenirSuggestionActiviteSoir } from "@/bibliotheque/api/famille";
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

  const { data: statut, isLoading: chargementStatut } = utiliserRequete(["garmin", "status"], async () => {
    const { data } = await clientApi.get<StatutGarmin>("/garmin/status");
    return data;
  });

  const { data: stats, isLoading: chargementStats } = utiliserRequete(["garmin", "stats"], async () => {
    const { data } = await clientApi.get<StatsGarmin>("/garmin/stats");
    return data;
  });

  const { data: suggestionSoir, isLoading: chargementSuggestion } = utiliserRequete(
    ["famille", "activites", "suggestion-soir"],
    obtenirSuggestionActiviteSoir,
    { enabled: Boolean(statut?.connected) }
  );

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

  if (chargementStatut || chargementStats) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Garmin santé & sport</h1>
          <p className="text-muted-foreground">Connexion, synchronisation et statistiques d'activité.</p>
        </div>
        <SkeletonPage ariaLabel="Chargement de l'espace Garmin" lignes={["h-28 w-full", "h-48 w-full"]} />
      </div>
    );
  }

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

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Activité du soir recommandée
          </CardTitle>
          <CardDescription>
            Proposition contextualisée avec la météo du jour et votre rythme Garmin récent.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!statut?.connected ? (
            <EtatVide
              Icone={Activity}
              titre="Connectez Garmin pour personnaliser la soirée"
              description="Une fois la synchronisation activée, l'app proposera automatiquement un créneau doux, modéré ou plus dynamique selon votre semaine."
              action={<Button size="sm" onClick={() => connecter()}>Connecter Garmin</Button>}
            />
          ) : chargementSuggestion ? (
            <SkeletonPage ariaLabel="Chargement de la suggestion du soir" lignes={["h-6 w-40", "h-4 w-full", "h-4 w-3/4"]} />
          ) : suggestionSoir ? (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">Énergie {suggestionSoir.niveau_energie}</Badge>
                <Badge variant="outline" className="gap-1">
                  <CloudSun className="h-3 w-3" />
                  {suggestionSoir.meteo}
                  {suggestionSoir.temperature_c != null ? ` · ${suggestionSoir.temperature_c}°C` : ""}
                </Badge>
              </div>
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="font-medium">{suggestionSoir.recommandation}</p>
                <p className="mt-1 text-sm text-muted-foreground">{suggestionSoir.raison}</p>
              </div>
              {!!suggestionSoir.alternatives?.length && (
                <div>
                  <p className="text-xs font-medium uppercase text-muted-foreground">Alternatives rapides</p>
                  <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                    {suggestionSoir.alternatives.map((alternative) => (
                      <li key={alternative}>• {alternative}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <EtatVide
              Icone={Sparkles}
              titre="Suggestion indisponible pour le moment"
              description="Réessayez après une synchronisation Garmin ou plus tard dans la journée."
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}