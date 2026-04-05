"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  Brush,
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
  const [categorieSelectionnee, setCategorieSelectionnee] = useState<string | null>(null);

  const classeHauteur =
    hauteur === 260
      ? "h-[260px]"
      : hauteur === 280
        ? "h-[280px]"
        : hauteur === 300
          ? "h-[300px]"
          : "h-[320px]";

  const selection = useMemo(
    () => donnees.find((item) => item.categorie === categorieSelectionnee) ?? null,
    [categorieSelectionnee, donnees]
  );

  if (!donnees.length) {
    return (
      <div className="flex h-[320px] items-center justify-center text-sm text-muted-foreground">
        Pas assez de donnees pour comparer budget prevu et reel.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className={classeHauteur}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={donnees} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
            <XAxis dataKey="categorie" tick={{ fontSize: 12 }} interval={0} angle={-20} textAnchor="end" height={56} />
            <YAxis tickFormatter={(value: number) => `${Math.round(value)} €`} tick={{ fontSize: 12 }} />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                const reel = Number(payload.find((item) => item.dataKey === "reel")?.value ?? 0);
                const prevu = Number(payload.find((item) => item.dataKey === "prevu")?.value ?? 0);
                const ecart = reel - prevu;

                return (
                  <div className="rounded-lg border bg-background/95 px-3 py-2 text-xs shadow-lg backdrop-blur">
                    <p className="font-semibold">{String(label)}</p>
                    <p className="text-muted-foreground">Prévu: {prevu.toFixed(2)} €</p>
                    <p className="text-muted-foreground">Réel: {reel.toFixed(2)} €</p>
                    <p className={ecart > 0 ? "text-destructive" : "text-emerald-600"}>
                      Écart: {ecart > 0 ? "+" : ""}
                      {ecart.toFixed(2)} €
                    </p>
                  </div>
                );
              }}
            />
            <Legend formatter={(value: string) => (value === "reel" ? "Réel" : "Prévu")} />
            <Bar
              dataKey="prevu"
              fill={COULEURS_GRAPHIQUES.muted}
              radius={[6, 6, 0, 0]}
              onClick={(entry: { payload?: DonneeBudgetVsReel }) =>
                setCategorieSelectionnee(entry.payload?.categorie ?? null)
              }
            />
            <Bar
              dataKey="reel"
              fill={COULEURS_GRAPHIQUES.accent1}
              radius={[6, 6, 0, 0]}
              onClick={(entry: { payload?: DonneeBudgetVsReel }) =>
                setCategorieSelectionnee(entry.payload?.categorie ?? null)
              }
            />
            <Brush dataKey="categorie" height={22} stroke={COULEURS_GRAPHIQUES.accent2} travellerWidth={10} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {selection ? (
        <div className="rounded-md border bg-muted/20 px-3 py-2 text-sm">
          <p className="font-medium">Détail {selection.categorie}</p>
          <p className="text-muted-foreground">
            Prévu {selection.prevu.toFixed(2)} € · Réel {selection.reel.toFixed(2)} € · Écart {selection.reel >= selection.prevu ? "+" : ""}
            {(selection.reel - selection.prevu).toFixed(2)} €
          </p>
        </div>
      ) : null}
    </div>
  );
}
