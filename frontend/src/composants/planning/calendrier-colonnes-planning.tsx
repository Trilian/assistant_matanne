"use client";

import { Fragment } from "react";
import { CalendarDays, Clock4 } from "lucide-react";

import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import type { RepasPlanning, TypeRepas } from "@/types/planning";

const CRENEAUX: Array<{ type: TypeRepas; heure: string; label: string; classes: string }> = [
  {
    type: "petit_dejeuner",
    heure: "08:00",
    label: "Petit-déjeuner",
    classes: "border-amber-200 bg-amber-50/70 dark:border-amber-900/40 dark:bg-amber-950/20",
  },
  {
    type: "dejeuner",
    heure: "12:00",
    label: "Déjeuner",
    classes: "border-emerald-200 bg-emerald-50/70 dark:border-emerald-900/40 dark:bg-emerald-950/20",
  },
  {
    type: "gouter",
    heure: "16:00",
    label: "Goûter",
    classes: "border-fuchsia-200 bg-fuchsia-50/70 dark:border-fuchsia-900/40 dark:bg-fuchsia-950/20",
  },
  {
    type: "diner",
    heure: "19:00",
    label: "Dîner",
    classes: "border-blue-200 bg-blue-50/70 dark:border-blue-900/40 dark:bg-blue-950/20",
  },
];

function trouverRepas(repasJour: RepasPlanning[], type: TypeRepas) {
  return repasJour.find((repas) => repas.type_repas === type);
}

export function CalendrierColonnesPlanning({
  dates,
  repasParJour,
}: {
  dates: string[];
  repasParJour: Record<string, RepasPlanning[]>;
}) {
  if (!dates.length) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <CalendarDays className="h-4 w-4 text-primary" />
          Planning en colonnes
        </CardTitle>
        <CardDescription>
          Vue style agenda pour balayer la semaine comme dans un calendrier visuel.
        </CardDescription>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <div className="grid min-w-[980px] grid-cols-[76px_repeat(7,minmax(0,1fr))] gap-2">
          <div />
          {dates.map((date) => {
            const estAujourdhui = date === new Date().toISOString().slice(0, 10);
            return (
              <div
                key={`header-${date}`}
                className={`rounded-xl border px-3 py-2 ${
                  estAujourdhui
                    ? "border-primary/40 bg-primary/5"
                    : "border-border bg-muted/30"
                }`}
              >
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  {new Date(date).toLocaleDateString("fr-FR", { weekday: "short" })}
                </p>
                <p className="font-semibold">
                  {new Date(date).toLocaleDateString("fr-FR", {
                    day: "numeric",
                    month: "short",
                  })}
                </p>
                {estAujourdhui ? (
                  <Badge className="mt-1" variant="secondary">
                    Aujourd&apos;hui
                  </Badge>
                ) : null}
              </div>
            );
          })}

          {CRENEAUX.map((creneau) => (
            <Fragment key={creneau.type}>
              <div className="flex min-h-[92px] flex-col items-end justify-start rounded-xl border border-dashed px-2 py-3 text-right">
                <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
                  <Clock4 className="h-3.5 w-3.5" />
                  {creneau.heure}
                </span>
                <span className="mt-1 text-[11px] text-muted-foreground">{creneau.label}</span>
              </div>

              {dates.map((date) => {
                const repas = trouverRepas(repasParJour[date] ?? [], creneau.type);
                return (
                  <div
                    key={`${date}-${creneau.type}`}
                    className={`min-h-[92px] rounded-xl border p-3 ${creneau.classes}`}
                  >
                    <p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                      {creneau.label}
                    </p>
                    {repas ? (
                      <div className="mt-2 space-y-2">
                        <p className="text-sm font-semibold leading-snug">
                          {repas.recette_nom || repas.notes || "Repas planifié"}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {repas.portions ? <Badge variant="outline">{repas.portions} pers.</Badge> : null}
                          {repas.nutri_score ? <Badge variant="secondary">Nutri {repas.nutri_score}</Badge> : null}
                        </div>
                        {repas.plat_jules ? (
                          <p className="text-xs text-muted-foreground">Version Jules : {repas.plat_jules}</p>
                        ) : null}
                      </div>
                    ) : (
                      <p className="mt-3 text-sm text-muted-foreground">Créneau libre</p>
                    )}
                  </div>
                );
              })}
            </Fragment>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
