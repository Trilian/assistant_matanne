// ═══════════════════════════════════════════════════════════
// Timeline — Vue chronologique de la semaine
// ═══════════════════════════════════════════════════════════

"use client";

import { CalendarDays, Utensils, ArrowLeft } from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserRequete } from "@/hooks/utiliser-api";
import { obtenirPlanningSemaine } from "@/lib/api/planning";
import type { TypeRepas } from "@/types/planning";

const LABELS_REPAS: Record<TypeRepas, string> = {
  petit_dejeuner: "🌅 Petit-déjeuner",
  dejeuner: "☀️ Déjeuner",
  gouter: "🍰 Goûter",
  diner: "🌙 Dîner",
};

const JOURS_SEMAINE = [
  "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
];

export default function PageTimeline() {
  const { data: planning, isLoading } = utiliserRequete(
    ["planning", "semaine"],
    () => obtenirPlanningSemaine()
  );

  // Trier les repas par date puis par type
  const repasOrdre: TypeRepas[] = ["petit_dejeuner", "dejeuner", "gouter", "diner"];
  const repasTries = [...(planning?.repas ?? [])].sort((a, b) => {
    const dateCompare = a.date.localeCompare(b.date);
    if (dateCompare !== 0) return dateCompare;
    return repasOrdre.indexOf(a.type_repas) - repasOrdre.indexOf(b.type_repas);
  });

  // Grouper par date
  const parDate: Record<string, typeof repasTries> = {};
  for (const repas of repasTries) {
    const key = repas.date.split("T")[0];
    if (!parDate[key]) parDate[key] = [];
    parDate[key].push(repas);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🕐 Timeline</h1>
          <p className="text-muted-foreground">
            Vue chronologique des repas de la semaine
          </p>
        </div>
        <Link href="/planning">
          <Button variant="outline" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Calendrier
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : Object.keys(parDate).length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <CalendarDays className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucun repas planifié cette semaine
          </CardContent>
        </Card>
      ) : (
        <div className="relative space-y-6">
          {/* Ligne de timeline */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

          {Object.entries(parDate).map(([dateStr, repas]) => {
            const d = new Date(dateStr);
            const jourNom = JOURS_SEMAINE[d.getDay()];
            const estAujourdhui =
              dateStr === new Date().toISOString().split("T")[0];

            return (
              <div key={dateStr} className="relative pl-10">
                {/* Point timeline */}
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
                    {repas.map((r) => (
                      <Card key={r.id} className="ml-2">
                        <CardContent className="flex items-center gap-3 py-3">
                          <Utensils className="h-4 w-4 text-muted-foreground shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-muted-foreground">
                              {LABELS_REPAS[r.type_repas] ?? r.type_repas}
                            </p>
                            <p className="text-sm font-medium truncate">
                              {r.recette_nom || r.notes || "—"}
                            </p>
                          </div>
                          {r.portions && (
                            <Badge variant="secondary" className="text-xs shrink-0">
                              {r.portions} pers.
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
      )}
    </div>
  );
}
