"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import type { RepasPlanning } from "@/types/planning";

interface CalendrierMensuelProps {
  mois: string;
  parJour: Record<string, RepasPlanning[]>;
}

const JOURS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];

function debutMois(mois: string): Date {
  return new Date(`${mois}-01T00:00:00`);
}

function formatJour(date: Date): string {
  return date.toISOString().split("T")[0];
}

function badgeType(typeRepas: string): string {
  if (typeRepas === "diner") return "🌙";
  if (typeRepas === "dejeuner") return "☀️";
  if (typeRepas === "petit_dejeuner") return "🌅";
  return "🍪";
}

export function CalendrierMensuel({ mois, parJour }: CalendrierMensuelProps) {
  const start = debutMois(mois);
  const year = start.getFullYear();
  const month = start.getMonth();

  const premierJour = new Date(year, month, 1);
  const dernierJour = new Date(year, month + 1, 0);

  const decalageDebut = (premierJour.getDay() + 6) % 7;
  const nbJours = dernierJour.getDate();
  const totalCellules = Math.ceil((decalageDebut + nbJours) / 7) * 7;

  const cellules: Array<Date | null> = [];
  for (let i = 0; i < totalCellules; i++) {
    const jour = i - decalageDebut + 1;
    if (jour < 1 || jour > nbJours) {
      cellules.push(null);
    } else {
      cellules.push(new Date(year, month, jour));
    }
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Vue mensuelle</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="grid grid-cols-7 gap-1">
          {JOURS.map((j) => (
            <div key={j} className="text-xs text-muted-foreground text-center py-1">
              {j}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {cellules.map((d, idx) => {
            if (!d) {
              return <div key={`empty-${idx}`} className="min-h-28 rounded-md bg-muted/30" />;
            }

            const key = formatJour(d);
            const repas = parJour[key] ?? [];
            const aujourdHui = key === new Date().toISOString().split("T")[0];

            return (
              <div
                key={key}
                className={`min-h-28 rounded-md border p-1.5 overflow-hidden ${aujourdHui ? "border-primary" : "border-border"}`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold">{d.getDate()}</span>
                  {repas.length > 0 && (
                    <Badge variant="secondary" className="text-[10px] h-4 px-1">
                      {repas.length}
                    </Badge>
                  )}
                </div>
                <div className="mt-1 space-y-1">
                  {repas.slice(0, 3).map((r) => (
                    <p key={`${r.id}-${r.type_repas}`} className="text-[10px] leading-tight truncate" title={r.recette_nom || r.notes || "Repas"}>
                      {badgeType(r.type_repas)} {r.recette_nom || r.notes || "Repas"}
                    </p>
                  ))}
                  {repas.length > 3 && (
                    <p className="text-[10px] text-muted-foreground">+{repas.length - 3}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
