"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import type { BacktestResultat } from "@/types/jeux";

interface BacktestResultatProps {
  data?: BacktestResultat;
  isLoading: boolean;
}

export function BacktestResultatCard({ data, isLoading }: BacktestResultatProps) {
  if (isLoading) return <Skeleton className="h-32 w-full" />;
  if (!data) return null;

  const tauxPct = (data.taux_reussite * 100).toFixed(1);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          📊 Backtest
          <Badge variant="secondary">{data.type_jeu}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xl font-bold">{data.nb_predictions}</p>
            <p className="text-xs text-muted-foreground">Prédictions</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xl font-bold">{data.nb_correctes}</p>
            <p className="text-xs text-muted-foreground">Correctes</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className={`text-xl font-bold ${parseFloat(tauxPct) > 50 ? "text-green-600" : "text-red-600"}`}>
              {tauxPct}%
            </p>
            <p className="text-xs text-muted-foreground">Taux réussite</p>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          En moyenne, un numéro en retard apparaît après {data.tirages_moyens.toFixed(1)} tirages
          (seuil value ≥ {data.seuil_value})
        </p>
        <p className="text-xs text-muted-foreground flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          {data.avertissement}
        </p>
      </CardContent>
    </Card>
  );
}
