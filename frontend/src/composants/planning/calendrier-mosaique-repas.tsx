"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import type { RepasPlanning, TypeRepas } from "@/types/planning";

const COULEUR_TYPE: Record<TypeRepas, string> = {
  petit_dejeuner: "bg-amber-100 text-amber-900 dark:bg-amber-950/30 dark:text-amber-100",
  dejeuner: "bg-emerald-100 text-emerald-900 dark:bg-emerald-950/30 dark:text-emerald-100",
  gouter: "bg-fuchsia-100 text-fuchsia-900 dark:bg-fuchsia-950/30 dark:text-fuchsia-100",
  diner: "bg-blue-100 text-blue-900 dark:bg-blue-950/30 dark:text-blue-100",
};

const LABEL_TYPE: Record<TypeRepas, string> = {
  petit_dejeuner: "Petit-dej",
  dejeuner: "Dejeuner",
  gouter: "Gouter",
  diner: "Diner",
};

const TYPES: TypeRepas[] = ["petit_dejeuner", "dejeuner", "gouter", "diner"];

interface CalendrierMosaiqueRepasProps {
  dates: string[];
  repasParJour: Record<string, RepasPlanning[]>;
}

function trouverRepasParType(repasJour: RepasPlanning[], type: TypeRepas): RepasPlanning | undefined {
  return repasJour.find((repas) => repas.type_repas === type);
}

export function CalendrierMosaiqueRepas({ dates, repasParJour }: CalendrierMosaiqueRepasProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Calendrier mosaique des repas</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
        {dates.map((date) => {
          const repasJour = repasParJour[date] ?? [];
          return (
            <div key={date} className="rounded-lg border p-2.5">
              <p className="mb-2 text-xs font-semibold text-muted-foreground">
                {new Date(date).toLocaleDateString("fr-FR", {
                  weekday: "short",
                  day: "numeric",
                  month: "short",
                })}
              </p>
              <div className="space-y-1.5">
                {TYPES.map((type) => {
                  const repas = trouverRepasParType(repasJour, type);
                  return (
                    <div
                      key={`${date}-${type}`}
                      className={`rounded-md px-2 py-1.5 text-[11px] ${COULEUR_TYPE[type]}`}
                      title={repas?.recette_nom || repas?.notes || `${LABEL_TYPE[type]} non planifie`}
                    >
                      <p className="font-semibold">{LABEL_TYPE[type]}</p>
                      <p className="truncate opacity-85">{repas?.recette_nom || repas?.notes || "Non planifie"}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
