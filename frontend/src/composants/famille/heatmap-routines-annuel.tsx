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
const NB_JOURS = 365;

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

      const poidsEtapes = Math.max(0.45, Math.min((routine.etapes?.length ?? 1) / 3, 1.35));

      if (routine.type === "matin") {
        return acc + (estWeekend ? 0.45 : 0.85) * poidsEtapes;
      }

      if (routine.type === "soir") {
        return acc + 0.7 * poidsEtapes;
      }

      return acc + (estWeekend ? 0.95 : 0.6) * poidsEtapes;
    }, 0),
    4
  );
}

function construireCellules(routines: Routine[]): CelluleHeatmap[] {
  const aujourdHui = new Date();
  aujourdHui.setHours(0, 0, 0, 0);

  return Array.from({ length: NB_JOURS }, (_, index) => {
    const date = new Date(aujourdHui);
    date.setDate(aujourdHui.getDate() - (NB_JOURS - 1 - index));

    return {
      cle: date.toISOString().split("T")[0],
      date,
      intensite: calculerIntensiteJour(date, routines),
    };
  });
}

function regrouperParSemaines(cellules: CelluleHeatmap[]): CelluleHeatmap[][] {
  const semaines: CelluleHeatmap[][] = [];

  for (const cellule of cellules) {
    const jourIndex = (cellule.date.getDay() + 6) % 7; // lundi = 0

    if (semaines.length === 0 || jourIndex === 0) {
      semaines.push([]);
    }

    semaines[semaines.length - 1].push(cellule);
  }

  return semaines;
}

export function HeatmapRoutinesAnnuel({ routines }: { routines: Routine[] }) {
  const routinesActives = routines.filter((routine) => routine.est_active !== false);
  const cellules = construireCellules(routinesActives);
  const semaines = regrouperParSemaines(cellules);
  const intensiteMax = Math.max(...cellules.map((cellule) => cellule.intensite), 1);
  const echelleCouleur = scaleLinear<number>().domain([0, intensiteMax]).range([0, 4]);
  const palette = [
    "bg-slate-200/60 dark:bg-slate-800/70",
    "bg-emerald-200/70 dark:bg-emerald-950/70",
    "bg-emerald-300/80 dark:bg-emerald-900/80",
    "bg-emerald-400/80 dark:bg-emerald-800/80",
    "bg-emerald-500/90 dark:bg-emerald-700/90",
  ];

  const joursTresActifs = cellules.filter((cellule) => cellule.intensite >= Math.max(2.5, intensiteMax * 0.65)).length;
  const totalEtapes = routinesActives.reduce((total, routine) => total + (routine.etapes?.length ?? 0), 0);

  return (
    <Card className="overflow-hidden border-emerald-200/70 bg-emerald-50/40 dark:border-emerald-900/50 dark:bg-emerald-950/10">
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle className="text-base">Vue annuelle des routines</CardTitle>
            <CardDescription>
              Une vue style GitHub sur 365 jours pour suivre la régularité des habitudes familiales.
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">365 derniers jours</Badge>
            <Badge variant="outline">{joursTresActifs} jours soutenus</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Routines actives</p>
            <p className="mt-1 text-lg font-semibold">{routinesActives.length}</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Étapes suivies</p>
            <p className="mt-1 text-lg font-semibold">{totalEtapes}</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Semaines visibles</p>
            <p className="mt-1 text-lg font-semibold">{semaines.length}</p>
          </div>
        </div>

        <div className="flex gap-3 overflow-x-auto pb-2">
          <div className="grid grid-rows-7 gap-1 pt-1 text-[10px] text-muted-foreground">
            {LIBELLES_JOURS.map((libelle, index) => (
              <span key={`${libelle}-${index}`} className="flex h-3 items-center">
                {libelle}
              </span>
            ))}
          </div>

          <div className="grid grid-flow-col grid-rows-7 gap-1">
            {semaines.flatMap((semaine, indexSemaine) => {
              const mapJour = new Map(
                semaine.map((cellule) => [((cellule.date.getDay() + 6) % 7), cellule])
              );

              return Array.from({ length: 7 }, (_, jourIndex) => {
                const cellule = mapJour.get(jourIndex);
                const intensiteNormalisee = Math.max(0, cellule?.intensite ?? 0);
                const niveau = Math.max(0, Math.min(4, Math.round(echelleCouleur(intensiteNormalisee))));
                const titre = cellule
                  ? `${cellule.date.toLocaleDateString("fr-FR")} • Intensité ${intensiteNormalisee.toFixed(1)}`
                  : "Jour hors plage";

                return (
                  <div
                    key={`${indexSemaine}-${jourIndex}`}
                    data-testid="heatmap-annuelle-cell"
                    title={titre}
                    className={`h-3 w-3 rounded-[3px] border border-emerald-200/40 dark:border-emerald-900/40 ${palette[niveau]}`}
                  />
                );
              });
            })}
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
          <span>Faible</span>
          <div className="flex gap-1">
            {palette.slice(1).map((classe, index) => (
              <span
                key={index}
                className={`h-2.5 w-4 rounded-sm border border-emerald-200/40 dark:border-emerald-900/40 ${classe}`}
              />
            ))}
          </div>
          <span>Élevée</span>
        </div>
      </CardContent>
    </Card>
  );
}
