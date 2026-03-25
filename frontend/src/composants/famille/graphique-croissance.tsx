"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
  CartesianGrid,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import type { PercentilesOMS } from "@/types/famille";

interface MesureJules {
  age_mois: number;
  valeur: number;
}

interface Props {
  age_mois: number;
  normes: Record<string, PercentilesOMS>;
  mesures?: MesureJules[];
}

type MetriqueType = "poids" | "taille" | "perimetre_cranien";

const METRICS_CONFIG: Record<
  MetriqueType,
  { label: string; unit: string; yLabel: string }
> = {
  poids: { label: "Poids", unit: "kg", yLabel: "Poids (kg)" },
  taille: { label: "Taille", unit: "cm", yLabel: "Taille (cm)" },
  perimetre_cranien: {
    label: "Périmètre crânien",
    unit: "cm",
    yLabel: "Périmètre (cm)",
  },
};

export function GraphiqueCroissance({ age_mois, normes, mesures = [] }: Props) {
  const [metrique, setMetrique] = useState<MetriqueType>("poids");

  const config = METRICS_CONFIG[metrique];
  const percentiles = normes[metrique] || {};

  // Générer les points de la courbe OMS (0 à age_mois + 3 pour la projection)
  const maxAge = Math.min(age_mois + 6, 36);
  const chartData = Array.from({ length: maxAge + 1 }, (_, i) => {
    const point: Record<string, number> = { age_mois: i };

    // Ajouter les percentiles OMS (constantes pour cet âge)
    if (percentiles.P3 !== undefined) point.P3 = percentiles.P3;
    if (percentiles.P15 !== undefined) point.P15 = percentiles.P15;
    if (percentiles.P50 !== undefined) point.P50 = percentiles.P50;
    if (percentiles.P85 !== undefined) point.P85 = percentiles.P85;
    if (percentiles.P97 !== undefined) point.P97 = percentiles.P97;

    // Ajouter la mesure de Jules si elle existe pour cet âge
    const mesure = mesures.find((m) => m.age_mois === i);
    if (mesure) {
      point.jules = mesure.valeur;
    }

    return point;
  });

  const hasData = chartData.some((d) => d.P50 !== undefined);

  if (!hasData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Croissance OMS</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Données OMS non disponibles pour cet âge.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="space-y-3 pb-3">
        <CardTitle className="text-sm">Croissance OMS — {config.label}</CardTitle>
        <div className="flex gap-2">
          {(Object.keys(METRICS_CONFIG) as MetriqueType[]).map((m) => (
            <Button
              key={m}
              size="sm"
              variant={metrique === m ? "default" : "outline"}
              onClick={() => setMetrique(m)}
            >
              {METRICS_CONFIG[m].label}
            </Button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(0, 0%, 85%)" />
            <XAxis
              dataKey="age_mois"
              tick={{ fontSize: 11 }}
              label={{ value: "Âge (mois)", position: "insideBottom", offset: -5 }}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={{ value: config.yLabel, angle: -90, position: "insideLeft" }}
            />
            <Tooltip
              formatter={(value, name) => {
                const numValue = Number(value);
                return [`${numValue.toFixed(1)} ${config.unit}`, String(name)];
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />

            {/* Courbes OMS */}
            <Line
              type="monotone"
              dataKey="P3"
              stroke="hsl(0, 70%, 60%)"
              strokeWidth={1.5}
              dot={false}
              name="P3"
              strokeDasharray="5 5"
            />
            <Line
              type="monotone"
              dataKey="P15"
              stroke="hsl(30, 80%, 50%)"
              strokeWidth={1.5}
              dot={false}
              name="P15"
              strokeDasharray="3 3"
            />
            <Line
              type="monotone"
              dataKey="P50"
              stroke="hsl(210, 70%, 50%)"
              strokeWidth={2.5}
              dot={false}
              name="P50"
            />
            <Line
              type="monotone"
              dataKey="P85"
              stroke="hsl(30, 80%, 50%)"
              strokeWidth={1.5}
              dot={false}
              name="P85"
              strokeDasharray="3 3"
            />
            <Line
              type="monotone"
              dataKey="P97"
              stroke="hsl(0, 70%, 60%)"
              strokeWidth={1.5}
              dot={false}
              name="P97"
              strokeDasharray="5 5"
            />

            {/* Mesures de Jules (si disponibles) */}
            {mesures.length > 0 && (
              <Line
                type="monotone"
                dataKey="jules"
                stroke="hsl(150, 70%, 40%)"
                strokeWidth={3}
                dot={{ r: 5, fill: "hsl(150, 70%, 40%)" }}
                name="Jules"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
        {mesures.length === 0 && (
          <p className="text-xs text-muted-foreground text-center mt-2">
            Ajoutez les mesures de Jules pour voir son évolution.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
