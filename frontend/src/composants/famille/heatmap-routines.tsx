"use client";

import { scaleLinear } from "d3-scale";
import { Badge } from "@/composants/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import type { Routine } from "@/types/famille";

const LIBELLES_JOURS = ["L", "M", "M", "J", "V", "S", "D"];
const NB_SEMAINES = 12;

type CelluleHeatmap = {
  cle: string;
  date: Date;
  intensite: number;
};

function calculerIntensiteJour(date: Date, routines: Routine[]): number {
  const jour = date.getDay();
  const estWeekend = jour === 0 || jour === 6;

  return Math.min(
    routines.reduce((acc, routine) => {
      if (routine.est_active === false) {
        return acc;
      }

      const poidsEtapes = Math.max(0.45, Math.min((routine.etapes?.length ?? 1) / 3, 1.25));

      if (routine.type === "matin") {
        return acc + (estWeekend ? 0.45 : 0.85) * poidsEtapes;
      }

      if (routine.type === "soir") {
        return acc + 0.7 * poidsEtapes;
      }

      return acc + (estWeekend ? 0.9 : 0.55) * poidsEtapes;
    }, 0),
    4
  );
}

function construireCellules(routines: Routine[]): CelluleHeatmap[] {
  const aujourdHui = new Date();
  aujourdHui.setHours(0, 0, 0, 0);

  return Array.from({ length: NB_SEMAINES * 7 }, (_, index) => {
    const date = new Date(aujourdHui);
    date.setDate(aujourdHui.getDate() - (NB_SEMAINES * 7 - 1 - index));

    return {
      cle: date.toISOString().split("T")[0],
      date,
      intensite: calculerIntensiteJour(date, routines),
    };
  });
}

export function HeatmapRoutines({ routines }: { routines: Routine[] }) {
  const routinesActives = routines.filter((routine) => routine.est_active !== false);
  const cellules = construireCellules(routinesActives);
  const intensiteMax = Math.max(...cellules.map((cellule) => cellule.intensite), 1);
  const echelleCouleur = scaleLinear<number>()
    .domain([0, intensiteMax])
    .range([0, 4]);
  const palette = [
    "bg-slate-200/60 dark:bg-slate-800/70",
    "bg-sky-200/70 dark:bg-sky-950/70",
    "bg-sky-300/80 dark:bg-sky-900/80",
    "bg-sky-400/80 dark:bg-sky-800/80",
    "bg-sky-500/90 dark:bg-sky-700/90",
  ];

  const totalEtapes = routinesActives.reduce(
    (total, routine) => total + (routine.etapes?.length ?? 0),
    0
  );

  const chargeParType = routinesActives.reduce(
    (acc, routine) => {
      const poids = Math.max(1, routine.etapes?.length ?? 1);
      acc[routine.type] += poids;
      return acc;
    },
    { matin: 0, soir: 0, journee: 0 }
  );

  const creneauPhare = Object.entries(chargeParType).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "matin";
  const libelleCreneau =
    creneauPhare === "journee"
      ? "Journée"
      : creneauPhare === "soir"
        ? "Soir"
        : "Matin";

  return (
    <Card className="overflow-hidden border-sky-200/70 bg-sky-50/40 dark:border-sky-900/50 dark:bg-sky-950/10">
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle className="text-base">Régularité des routines</CardTitle>
            <CardDescription>
              Aperçu visuel glissant sur trois mois pour repérer les créneaux les plus chargés.
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">12 dernières semaines</Badge>
            <Badge variant="outline">{routinesActives.length} routine(s) actives</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Créneau fort</p>
            <p className="mt-1 text-lg font-semibold">{libelleCreneau}</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Étapes suivies</p>
            <p className="mt-1 text-lg font-semibold">{totalEtapes}</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Charge moyenne</p>
            <p className="mt-1 text-lg font-semibold">
              {Math.round(cellules.reduce((total, cellule) => total + cellule.intensite, 0) / cellules.length * 100) / 100}
            </p>
          </div>
        </div>

        <div className="flex gap-3 overflow-x-auto pb-1">
          <div className="grid grid-rows-7 gap-1 pt-6 text-[10px] text-muted-foreground">
            {LIBELLES_JOURS.map((libelle, index) => (
              <span key={`${libelle}-${index}`} className="flex h-3 items-center">
                {libelle}
              </span>
            ))}
          </div>

          <div className="grid grid-flow-col grid-rows-7 gap-1">
            {cellules.map((cellule) => {
              const intensiteNormalisee = Math.max(0, cellule.intensite);
              const titre = `${cellule.date.toLocaleDateString("fr-FR")} • Intensité ${intensiteNormalisee.toFixed(1)}`;
              const niveau = Math.max(0, Math.min(4, Math.round(echelleCouleur(intensiteNormalisee))));

              return (
                <div
                  key={cellule.cle}
                  data-testid="heatmap-cell"
                  title={titre}
                  className={`h-3 w-3 rounded-[3px] border border-sky-200/40 dark:border-sky-900/40 ${palette[niveau]}`}
                />
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          <span>Moins dense</span>
          <div className="flex gap-1">
            {palette.slice(1).map((classe, index) => (
              <span
                key={index}
                className={`h-2.5 w-4 rounded-sm border border-sky-200/40 dark:border-sky-900/40 ${classe}`}
              />
            ))}
          </div>
          <span>Plus dense</span>
        </div>
      </CardContent>
    </Card>
  );
}
