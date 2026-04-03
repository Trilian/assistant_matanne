"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { COULEURS_GRAPHIQUES } from "@/bibliotheque/theme-graphiques";

export interface DonneeBudgetVsReel {
  categorie: string;
  reel: number;
  prevu: number;
}

interface GraphiqueBudgetVsReelProps {
  donnees: DonneeBudgetVsReel[];
  hauteur?: number;
}

export function GraphiqueBudgetVsReel({
  donnees,
  hauteur = 320,
}: GraphiqueBudgetVsReelProps) {
  const classeHauteur =
    hauteur === 260
      ? "h-[260px]"
      : hauteur === 280
        ? "h-[280px]"
        : hauteur === 300
          ? "h-[300px]"
          : "h-[320px]";

  if (!donnees.length) {
    return (
      <div className="flex h-[320px] items-center justify-center text-sm text-muted-foreground">
        Pas assez de donnees pour comparer budget prevu et reel.
      </div>
    );
  }

  return (
    <div className={classeHauteur}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={donnees} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
          <XAxis dataKey="categorie" tick={{ fontSize: 12 }} interval={0} angle={-20} textAnchor="end" height={56} />
          <YAxis tickFormatter={(value: number) => `${Math.round(value)} €`} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value, name) => [
              typeof value === "number" ? `${value.toFixed(2)} €` : "—",
              name === "reel" ? "Réel" : "Prévu",
            ]}
          />
          <Legend formatter={(value: string) => (value === "reel" ? "Réel" : "Prévu")} />
          <Bar dataKey="prevu" fill={COULEURS_GRAPHIQUES.muted} radius={[6, 6, 0, 0]} />
          <Bar dataKey="reel" fill={COULEURS_GRAPHIQUES.accent1} radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
