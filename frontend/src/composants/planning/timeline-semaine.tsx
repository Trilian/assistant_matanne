"use client";

import { Utensils } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent } from "@/composants/ui/card";
import type { RepasPlanning, TypeRepas } from "@/types/planning";

const LABELS_REPAS: Record<TypeRepas, string> = {
  petit_dejeuner: "🌅 Petit-déjeuner",
  dejeuner: "☀️ Déjeuner",
  gouter: "🍰 Goûter",
  diner: "🌙 Dîner",
};

const JOURS_SEMAINE = [
  "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
];

interface TimelineSemaineProps {
  repas: RepasPlanning[];
}

export function TimelineSemaine({ repas }: TimelineSemaineProps) {
  const repasOrdre: TypeRepas[] = ["petit_dejeuner", "dejeuner", "gouter", "diner"];
  const repasTries = [...repas].sort((a, b) => {
    const dateCompare = (a.date ?? a.date_repas ?? "").localeCompare(b.date ?? b.date_repas ?? "");
    if (dateCompare !== 0) return dateCompare;
    return repasOrdre.indexOf(a.type_repas) - repasOrdre.indexOf(b.type_repas);
  });

  const parDate: Record<string, RepasPlanning[]> = {};
  for (const repasItem of repasTries) {
    const key = (repasItem.date ?? repasItem.date_repas ?? "").split("T")[0];
    if (!parDate[key]) parDate[key] = [];
    parDate[key].push(repasItem);
  }

  return (
    <div className="relative space-y-6">
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

      {Object.entries(parDate).map(([dateStr, repasDate]) => {
        const d = new Date(dateStr);
        const jourNom = JOURS_SEMAINE[d.getDay()];
        const estAujourdhui = dateStr === new Date().toISOString().split("T")[0];

        return (
          <div key={dateStr} className="relative pl-10">
            <div
              className={`absolute left-2.5 top-1 h-3 w-3 rounded-full border-2 ${
                estAujourdhui
                  ? "bg-primary border-primary"
                  : "bg-background border-muted-foreground"
              }`}
            />

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <h2
                  className={`text-sm font-semibold ${
                    estAujourdhui ? "text-primary" : ""
                  }`}
                >
                  {jourNom}
                </h2>
                <span className="text-xs text-muted-foreground">
                  {d.toLocaleDateString("fr-FR", {
                    day: "numeric",
                    month: "long",
                  })}
                </span>
                {estAujourdhui && (
                  <Badge variant="default" className="text-xs">
                    Aujourd&apos;hui
                  </Badge>
                )}
              </div>

              <div className="space-y-2">
                {repasDate.map((item) => (
                  <Card key={item.id} className="ml-2">
                    <CardContent className="flex items-center gap-3 py-3">
                      <Utensils className="h-4 w-4 text-muted-foreground shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-muted-foreground">
                          {LABELS_REPAS[item.type_repas] ?? item.type_repas}
                        </p>
                        <p className="text-sm font-medium truncate">
                          {item.recette_nom || item.notes || "—"}
                        </p>
                      </div>
                      {item.portions && (
                        <Badge variant="secondary" className="text-xs shrink-0">
                          {item.portions} pers.
                        </Badge>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
