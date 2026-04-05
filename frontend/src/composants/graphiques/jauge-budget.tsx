"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { JaugeScoreBienEtre } from "@/composants/graphiques/jauge-score-bien-etre";

interface JaugeBudgetProps {
  totalMois: number;
  budgetCible?: number;
}

export function JaugeBudget({ totalMois, budgetCible = 2500 }: JaugeBudgetProps) {
  const ratio = budgetCible > 0 ? totalMois / budgetCible : 0;
  const score = Math.max(0, Math.min(100, Math.round((1 - Math.max(0, ratio - 1)) * 100)));
  const pourcentageUtilise = Math.round(ratio * 100);
  const restant = Math.max(0, budgetCible - totalMois);
  const depassement = Math.max(0, totalMois - budgetCible);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Jauge budget mensuel</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-col items-center gap-2">
          <JaugeScoreBienEtre score={score} />
          <p className="text-xs text-muted-foreground">Maîtrise budgétaire</p>
        </div>

        <div className="grid flex-1 gap-3 sm:grid-cols-2">
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Dépensé ce mois</p>
            <p className="mt-1 text-xl font-semibold">{totalMois.toFixed(2)} €</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Budget cible</p>
            <p className="mt-1 text-xl font-semibold">{budgetCible.toFixed(2)} €</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">Utilisation</p>
            <p className="mt-1 text-xl font-semibold">{pourcentageUtilise}%</p>
          </div>
          <div className="rounded-xl border bg-background/70 p-3">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              {depassement > 0 ? "Dépassement" : "Reste à dépenser"}
            </p>
            <p className="mt-1 text-xl font-semibold">
              {(depassement > 0 ? depassement : restant).toFixed(2)} €
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
