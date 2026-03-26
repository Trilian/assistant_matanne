"use client";

import { useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import dynamic from "next/dynamic";

// Import dynamique Recharts (SSR disabled)
const LineChart = dynamic(
  () => import("recharts").then((mod) => mod.LineChart),
  { ssr: false, loading: () => <Skeleton className="h-64 w-full" /> }
);
const Line = dynamic(() => import("recharts").then((mod) => mod.Line), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then((mod) => mod.CartesianGrid), { ssr: false });
const XAxis = dynamic(() => import("recharts").then((mod) => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then((mod) => mod.YAxis), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then((mod) => mod.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then((mod) => mod.Legend), { ssr: false });

export interface PointCote {
  timestamp: string;
  cote_domicile: number | null;
  cote_nul: number | null;
  cote_exterieur: number | null;
  cote_over_25?: number | null;
  cote_under_25?: number | null;
  bookmaker: string;
}

interface HeatmapCotesProps {
  points: PointCote[];
  matchInfo?: string;
}

export function HeatmapCotes({ points, matchInfo }: HeatmapCotesProps) {
  const data = useMemo(() => {
    if (!points || points.length === 0) return [];

    return points.map((p) => ({
      heure: new Date(p.timestamp).toLocaleTimeString("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
      "Cote 1": p.cote_domicile,
      "Cote N": p.cote_nul,
      "Cote 2": p.cote_exterieur,
      "Over 2.5": p.cote_over_25,
      "Under 2.5": p.cote_under_25,
    }));
  }, [points]);

  if (!points || points.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Évolution des cotes</CardTitle>
          {matchInfo && <CardDescription>{matchInfo}</CardDescription>}
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Aucune donnée d'historique disponible pour ce match
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Évolution des cotes bookmaker</CardTitle>
        {matchInfo && <CardDescription>{matchInfo}</CardDescription>}
        <p className="text-xs text-muted-foreground">
          {points.length} captures • Source: {points[0]?.bookmaker || "Betclic"}
        </p>
      </CardHeader>
      <CardContent>
        <div className="w-full h-64">
          <LineChart width={600} height={250} data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="heure" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "6px",
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line
              type="monotone"
              dataKey="Cote 1"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Cote N"
              stroke="#64748b"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Cote 2"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="Over 2.5"
              stroke="#10b981"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="Under 2.5"
              stroke="#f59e0b"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
            />
          </LineChart>
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          💡 Une chute brutale de cote peut indiquer une info importante (blessure, tactique...)
        </p>
      </CardContent>
    </Card>
  );
}
