// ═══════════════════════════════════════════════════════════
// Ma Journée — Vue unifiée de la journée
// Repas + Tâches + Routines + Météo + Anniversaires
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useState } from "react";
import {
  Sun,
  Cloud,
  ChefHat,
  CheckCircle2,
  RotateCw,
  Cake,
  ArrowRight,
  Clock,
  Droplets,
  Wind,
} from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirTableauBord } from "@/bibliotheque/api/tableau-bord";
import { obtenirTachesJourMaison, modifierTacheEntretien } from "@/bibliotheque/api/maison";
import { listerActivites } from "@/bibliotheque/api/famille";
import { clientApi } from "@/bibliotheque/api/client";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { utiliserMutation } from "@/crochets/utiliser-api";
import { toast } from "sonner";

type MeteoData = {
  ville: string;
  temperature: number;
  description: string;
  humidite: number;
  vent: number;
  icone: string;
};

type AnniversaireAujourdhui = {
  id: number;
  nom_personne: string;
  age?: number;
  relation: string;
};

type RoutineEtape = {
  id: number;
  titre: string;
  duree_minutes?: number;
  est_terminee: boolean;
};

type RoutineJour = {
  id: number;
  nom: string;
  type: string;
  etapes: RoutineEtape[];
};

export default function PageMaJournee() {
  const { utilisateur } = utiliserAuth();
  const aujourdhui = new Date().toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  const { data: dashboard, isLoading: chargementDashboard } = utiliserRequete(
    ["tableau-bord"],
    obtenirTableauBord
  );

  const { data: tachesJour, refetch: rechargerTaches } = utiliserRequete(
    ["maison", "taches-jour"],
    obtenirTachesJourMaison
  );

  const { data: activites } = utiliserRequete(["famille", "activites", "aujourdhui"], () =>
    listerActivites(undefined, new Date().toISOString().split("T")[0])
  );

  const { data: routines } = utiliserRequete<RoutineJour[]>(
    ["famille", "routines", "jour"],
    async () => {
      const { data } = await clientApi.get<{ items: RoutineJour[] }>("/famille/routines", {
        params: { est_active: true },
      });
      return data.items ?? [];
    }
  );

  const { data: anniversaires } = utiliserRequete<AnniversaireAujourdhui[]>(
    ["famille", "anniversaires", "aujourdhui"],
    async () => {
      const { data } = await clientApi.get<{ items: AnniversaireAujourdhui[] }>(
        "/famille/anniversaires/aujourd-hui"
      );
      return data.items ?? [];
    }
  );

  const [meteo, setMeteo] = useState<MeteoData | null>(null);

  useEffect(() => {
    let annule = false;
    async function chargerMeteo() {
      try {
        const res = await fetch("https://wttr.in/Paris?format=j1");
        if (!res.ok) return;
        const json = await res.json();
        const actuel = json.current_condition?.[0];
        if (!actuel || annule) return;
        setMeteo({
          ville: json.nearest_area?.[0]?.areaName?.[0]?.value ?? "Paris",
          temperature: Number(actuel.temp_C ?? 0),
          description: actuel.weatherDesc?.[0]?.value ?? "",
          humidite: Number(actuel.humidity ?? 0),
          vent: Number(actuel.windspeedKmph ?? 0),
          icone: actuel.weatherCode ?? "",
        });
      } catch {
        if (!annule) setMeteo(null);
      }
    }
    chargerMeteo();
    return () => { annule = true; };
  }, []);

  const { mutate: validerTache, isPending: validationEnCours } = utiliserMutation(
    async ({ id, fait }: { id: number; fait: boolean }) =>
      modifierTacheEntretien(id, { fait }),
    {
      onSuccess: () => {
        void rechargerTaches();
        toast.success("Tâche mise à jour");
      },
    }
  );

  const repas = dashboard?.repas_aujourd_hui ?? [];
  const taches = (tachesJour ?? []).slice(0, 8);
  const routinesMatin = (routines ?? []).filter((r) => r.type === "matin");
  const routinesSoir = (routines ?? []).filter((r) => r.type === "soir");

  const heure = new Date().getHours();
  const salutation =
    heure < 12 ? "Bonjour" : heure < 18 ? "Bon après-midi" : "Bonsoir";

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* En-tête jour */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">
          {salutation} {utilisateur?.nom ?? ""} 👋
        </h1>
        <p className="text-muted-foreground capitalize">{aujourdhui}</p>
      </div>

      {/* Météo */}
      {meteo && (
        <Card className="border-sky-300/50 bg-gradient-to-r from-sky-50 to-blue-50 dark:from-sky-950/30 dark:to-blue-950/20">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {meteo.temperature > 20 ? (
                  <Sun className="h-8 w-8 text-amber-500" />
                ) : (
                  <Cloud className="h-8 w-8 text-sky-500" />
                )}
                <div>
                  <p className="text-3xl font-bold">{meteo.temperature}°C</p>
                  <p className="text-sm text-muted-foreground">{meteo.description}</p>
                </div>
              </div>
              <div className="text-right text-xs text-muted-foreground space-y-1">
                <p className="flex items-center gap-1 justify-end">
                  <Droplets className="h-3 w-3" /> {meteo.humidite}%
                </p>
                <p className="flex items-center gap-1 justify-end">
                  <Wind className="h-3 w-3" /> {meteo.vent} km/h
                </p>
                <p className="text-[11px]">{meteo.ville}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Anniversaires du jour */}
      {anniversaires && anniversaires.length > 0 && (
        <Card className="border-pink-300/50 bg-pink-50/50 dark:border-pink-900/40 dark:bg-pink-950/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Cake className="h-4 w-4 text-pink-500" />
              Anniversaire{anniversaires.length > 1 ? "s" : ""} du jour 🎉
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {anniversaires.map((a) => (
              <div key={a.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{a.nom_personne}</p>
                  <p className="text-xs text-muted-foreground">
                    {a.relation}{a.age ? ` · ${a.age} ans` : ""}
                  </p>
                </div>
                <span className="text-2xl">🎂</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Repas du jour */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <ChefHat className="h-4 w-4" />
            Repas du jour
          </CardTitle>
        </CardHeader>
        <CardContent>
          {chargementDashboard ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : repas.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground mb-2">Aucun repas planifié</p>
              <Button variant="outline" size="sm" asChild>
                <Link href="/cuisine/ma-semaine">Planifier mes repas</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              {repas.map((r, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-md border px-3 py-2"
                >
                  <div>
                    <Badge variant="outline" className="text-xs capitalize mr-2">
                      {r.type_repas}
                    </Badge>
                    <span className="text-sm font-medium">
                      {r.recette_nom ?? "Non défini"}
                    </span>
                  </div>
                </div>
              ))}
              <Button variant="ghost" size="sm" className="-ml-2" asChild>
                <Link href="/cuisine/ma-semaine" className="flex items-center gap-1">
                  Voir la semaine <ArrowRight className="h-3 w-3" />
                </Link>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Routines du matin */}
      {routinesMatin.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <Sun className="h-4 w-4 text-amber-500" />
              Routine du matin
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {routinesMatin[0].etapes.map((etape) => (
                <div
                  key={etape.id}
                  className="flex items-center gap-2 text-sm"
                >
                  <CheckCircle2
                    className={`h-4 w-4 shrink-0 ${
                      etape.est_terminee
                        ? "text-green-500"
                        : "text-muted-foreground"
                    }`}
                  />
                  <span className={etape.est_terminee ? "line-through text-muted-foreground" : ""}>
                    {etape.titre}
                  </span>
                  {etape.duree_minutes && (
                    <span className="text-xs text-muted-foreground ml-auto flex items-center gap-0.5">
                      <Clock className="h-3 w-3" /> {etape.duree_minutes} min
                    </span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tâches du jour */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Tâches du jour
            {taches.length > 0 && (
              <Badge variant="secondary" className="ml-1">
                {taches.filter((t) => !t.fait).length} restante(s)
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {taches.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-3">
              Aucune tâche pour aujourd&apos;hui ✨
            </p>
          ) : (
            <div className="space-y-2">
              {taches.map((tache) => (
                <div
                  key={`${tache.nom}-${tache.id_source}`}
                  className="flex items-center justify-between rounded-md border px-3 py-2"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <button
                      type="button"
                      className="shrink-0"
                      disabled={!tache.id_source || validationEnCours}
                      onClick={() => {
                        if (tache.id_source)
                          validerTache({ id: tache.id_source, fait: !tache.fait });
                      }}
                    >
                      <CheckCircle2
                        className={`h-5 w-5 ${
                          tache.fait
                            ? "text-green-500"
                            : "text-muted-foreground hover:text-green-400"
                        }`}
                      />
                    </button>
                    <span
                      className={`text-sm truncate ${
                        tache.fait ? "line-through text-muted-foreground" : ""
                      }`}
                    >
                      {tache.nom}
                    </span>
                  </div>
                  {tache.categorie && (
                    <Badge variant="outline" className="text-xs shrink-0 ml-2">
                      {tache.categorie}
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          )}
          <Button variant="ghost" size="sm" className="-ml-2 mt-2" asChild>
            <Link href="/maison/entretien" className="flex items-center gap-1">
              Toutes les tâches <ArrowRight className="h-3 w-3" />
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Activités prévues */}
      {activites && activites.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <RotateCw className="h-4 w-4" />
              Activités prévues
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {activites.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between rounded-md border px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium">{a.titre}</p>
                  {a.lieu && (
                    <p className="text-xs text-muted-foreground">📍 {a.lieu}</p>
                  )}
                </div>
                <div className="text-right text-xs text-muted-foreground">
                  <Badge variant="outline" className="capitalize">{a.type}</Badge>
                  {a.duree_minutes && (
                    <p className="mt-1">{a.duree_minutes} min</p>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Routines du soir */}
      {routinesSoir.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base flex items-center gap-2">
              <RotateCw className="h-4 w-4 text-indigo-500" />
              Routine du soir
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-1.5">
              {routinesSoir[0].etapes.map((etape) => (
                <div
                  key={etape.id}
                  className="flex items-center gap-2 text-sm"
                >
                  <CheckCircle2
                    className={`h-4 w-4 shrink-0 ${
                      etape.est_terminee
                        ? "text-green-500"
                        : "text-muted-foreground"
                    }`}
                  />
                  <span className={etape.est_terminee ? "line-through text-muted-foreground" : ""}>
                    {etape.titre}
                  </span>
                  {etape.duree_minutes && (
                    <span className="text-xs text-muted-foreground ml-auto flex items-center gap-0.5">
                      <Clock className="h-3 w-3" /> {etape.duree_minutes} min
                    </span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
