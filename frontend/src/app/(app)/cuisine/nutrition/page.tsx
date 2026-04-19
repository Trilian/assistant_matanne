// ═══════════════════════════════════════════════════════════
// Nutrition Hebdomadaire — Suivi macros semaine
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  Flame,
  Beef,
  Droplets,
  Wheat,
  ChevronLeft,
  AlertCircle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Progress } from "@/composants/ui/progress";
import { EtatVide } from "@/composants/ui/etat-vide";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { SwipeableItem } from "@/composants/swipeable-item";
import {
  obtenirNutritionHebdo,
  type NutritionHebdo,
} from "@/bibliotheque/api/planning";
import { obtenirPreferences } from "@/bibliotheque/api/preferences";
import { HeatmapNutritionnel } from "@/composants/graphiques/heatmap-nutritionnel";
import { RadarNutritionFamille } from "@/composants/graphiques/radar-nutrition-famille";

// Valeurs par défaut utilisées pendant le chargement des préférences
const OBJECTIFS_DEFAUT = {
  calories: 2000,
  proteines: 60,
  lipides: 70,
  glucides: 260,
};

function formatDate(iso: string): string {
  return new Date(iso + "T00:00:00").toLocaleDateString("fr-FR", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });
}

function pourcentage(valeur: number, objectif: number): number {
  return Math.min(Math.round((valeur / objectif) * 100), 150);
}

function couleurPct(pct: number): string {
  if (pct >= 90 && pct <= 110) return "bg-green-500";
  if (pct >= 70) return "bg-orange-400";
  return "bg-red-400";
}

function BarreProgression({
  valeur,
  objectif,
  label,
  unite,
}: {
  valeur: number;
  objectif: number;
  label: string;
  unite: string;
}) {
  const pct = pourcentage(valeur, objectif);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">
          {Math.round(valeur)} / {objectif} {unite}
        </span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <Progress value={Math.min(pct, 100)} className={`h-2 ${couleurPct(pct)}`} />
      </div>
    </div>
  );
}

function ContenuNutrition() {
  const [decalageSemaine, setDecalageSemaine] = useState(0);

  const semaine =
    decalageSemaine === 0
      ? undefined
      : (() => {
          const d = new Date();
          d.setDate(d.getDate() + decalageSemaine * 7);
          return d.toISOString().slice(0, 10);
        })();

  const { data, isLoading } = utiliserRequete<NutritionHebdo>(
    ["nutrition-hebdo", String(decalageSemaine)],
    () => obtenirNutritionHebdo(semaine)
  );

  const { data: prefs } = utiliserRequete(
    ["preferences"],
    obtenirPreferences
  );

  const objectifs = {
    calories: prefs?.objectif_calories ?? OBJECTIFS_DEFAUT.calories,
    proteines: prefs?.objectif_proteines ?? OBJECTIFS_DEFAUT.proteines,
    lipides: prefs?.objectif_lipides ?? OBJECTIFS_DEFAUT.lipides,
    glucides: prefs?.objectif_glucides ?? OBJECTIFS_DEFAUT.glucides,
  };

  const jours = data ? Object.entries(data.par_jour ?? {}).sort(([a], [b]) => a.localeCompare(b)) : [];

  const donneesHeatmap = jours.map(([dateIso, valeur]) => {
    const caloriesPct = Math.min(100, (valeur.calories / objectifs.calories) * 100);
    const proteinesPct = Math.min(100, (valeur.proteines / objectifs.proteines) * 100);
    const score = Math.round((caloriesPct * 0.6) + (proteinesPct * 0.4));
    return {
      date: dateIso,
      score,
      repas_planifies: valeur.repas.length,
      details: `${Math.round(valeur.calories)} kcal · ${Math.round(valeur.proteines)}g prot.`,
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/cuisine">
            <ChevronLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Nutrition hebdomadaire</h1>
          {data && (
            <p className="text-sm text-muted-foreground">
              {formatDate(data.semaine_debut)} → {formatDate(data.semaine_fin)}
            </p>
          )}
        </div>
      </div>

      {/* Navigation semaine */}
      <div className="flex items-center justify-center gap-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setDecalageSemaine((s) => s - 1)}
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Semaine préc.
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={decalageSemaine === 0}
          onClick={() => setDecalageSemaine(0)}
        >
          Cette semaine
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={decalageSemaine >= 0}
          onClick={() => setDecalageSemaine((s) => s + 1)}
        >
          Semaine suiv. <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
      ) : data ? (
        <>
          {/* Totaux semaine */}
          <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
            <Card>
              <CardContent className="pt-4 text-center">
                <Flame className="h-6 w-6 mx-auto mb-1 text-orange-500" />
                <p className="text-2xl font-bold">
                  {Math.round(data.moyenne_calories_par_jour)}
                </p>
                <p className="text-xs text-muted-foreground">
                  kcal / jour (moy.)
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 text-center">
                <Beef className="h-6 w-6 mx-auto mb-1 text-red-500" />
                <p className="text-2xl font-bold">
                  {Math.round(data.totaux.proteines)}g
                </p>
                <p className="text-xs text-muted-foreground">
                  protéines (sem.)
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 text-center">
                <Droplets className="h-6 w-6 mx-auto mb-1 text-yellow-500" />
                <p className="text-2xl font-bold">
                  {Math.round(data.totaux.lipides)}g
                </p>
                <p className="text-xs text-muted-foreground">
                  lipides (sem.)
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4 text-center">
                <Wheat className="h-6 w-6 mx-auto mb-1 text-amber-600" />
                <p className="text-2xl font-bold">
                  {Math.round(data.totaux.glucides)}g
                </p>
                <p className="text-xs text-muted-foreground">
                  glucides (sem.)
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Calendrier nutritionnel</CardTitle>
            </CardHeader>
            <CardContent>
              <HeatmapNutritionnel donnees={donneesHeatmap} mois={3} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Radar nutritionnel famille</CardTitle>
            </CardHeader>
            <CardContent>
              <RadarNutritionFamille totaux={data.totaux} nbJours={jours.length || 7} />
            </CardContent>
          </Card>

          {/* Alerte repas sans données */}
          {data.nb_repas_sans_donnees > 0 && (
            <div className="flex items-center gap-2 rounded-lg border border-orange-200 bg-orange-50 p-3 text-sm text-orange-700 dark:border-orange-800 dark:bg-orange-950 dark:text-orange-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>
                {data.nb_repas_sans_donnees} repas sur {data.nb_repas_total}{" "}
                n&apos;ont pas de données nutritionnelles.
              </span>
            </div>
          )}

          {/* Détail par jour */}
          <div className="space-y-3">
            <h2 className="text-lg font-semibold">Détail par jour</h2>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {jours.map(([dateStr, jour]) => (
                <SwipeableItem
                  key={dateStr}
                  desactiverGauche
                  labelDroit="Voir planning"
                  onSwipeRight={() => {
                    window.location.href = "/cuisine/planning";
                  }}
                >
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm font-medium capitalize">
                        {formatDate(dateStr)}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <BarreProgression
                        valeur={jour.calories}
                        objectif={objectifs.calories}
                        label="Calories"
                        unite="kcal"
                      />
                      <BarreProgression
                        valeur={jour.proteines}
                        objectif={objectifs.proteines}
                        label="Protéines"
                        unite="g"
                      />
                      <BarreProgression
                        valeur={jour.lipides}
                        objectif={objectifs.lipides}
                        label="Lipides"
                        unite="g"
                      />
                      <BarreProgression
                        valeur={jour.glucides}
                        objectif={objectifs.glucides}
                        label="Glucides"
                        unite="g"
                      />
                      {jour.repas.length > 0 && (
                        <div className="pt-1 space-y-0.5">
                          {jour.repas.map((r) => (
                            <div
                              key={r.id}
                              className="flex items-center justify-between text-xs text-muted-foreground"
                            >
                              <span className="truncate max-w-[140px]">
                                {r.nom_recette ?? r.type}
                              </span>
                              {r.calories != null && (
                                <Badge variant="secondary" className="text-[10px]">
                                  {r.calories} kcal
                                </Badge>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </SwipeableItem>
              ))}
            </div>
          </div>
        </>
      ) : (
        <Card>
          <CardContent className="py-6">
            <EtatVide
              Icone={AlertCircle}
              titre="Aucune donnée nutritionnelle"
              description="Planifie quelques repas cette semaine pour obtenir le suivi macros et les visualisations." 
              action={
                <Link href="/cuisine/planning" className="text-primary underline mt-1 inline-block">
                  Planifier des repas
                </Link>
              }
              className="border-0 bg-muted/20 py-6"
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function PageNutrition() {
  return <ContenuNutrition />;
}
