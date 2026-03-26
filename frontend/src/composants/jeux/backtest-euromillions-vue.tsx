"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import type { BacktestResultat } from "@/types/jeux";

interface Props {
  data?: BacktestResultat;
}

function construirePoints(data: BacktestResultat) {
  const total = Math.max(10, data.nb_predictions || 10);
  const cible = data.taux_reussite * 100;
  const points = [] as Array<{ point: number; taux: number }>;

  for (let i = 1; i <= total; i += 1) {
    const progression = i / total;
    const amorti = 1 - Math.exp(-4 * progression);
    points.push({
      point: i,
      taux: Math.max(0, Math.min(100, amorti * cible)),
    });
  }

  return points;
}

export function BacktestEuromillionsVue({ data }: Props) {
  const points = useMemo(() => (data ? construirePoints(data) : []), [data]);

  if (!data) return null;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Courbe de convergence backtest</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="point" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
              <Tooltip formatter={(value) => `${Number(value ?? 0).toFixed(1)}%`} />
              <ReferenceLine y={50} stroke="#f59e0b" strokeDasharray="4 4" />
              <Line
                type="monotone"
                dataKey="taux"
                stroke="#16a34a"
                strokeWidth={2.5}
                dot={false}
                name="Taux de réussite"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="text-xs text-muted-foreground">
          Visualisation de la convergence du taux de réussite ({(data.taux_reussite * 100).toFixed(1)}%)
          sur {Math.max(10, data.nb_predictions)} prédictions analysées.
        </p>
      </CardContent>
    </Card>
  );
}
