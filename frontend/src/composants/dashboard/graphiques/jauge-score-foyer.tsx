"use client";

import { Activity, Utensils, Wallet, Wrench, RotateCcw } from "lucide-react";

interface JaugeScoreFoyerProps {
  score: number;
  composantes: {
    nutrition: number;
    budget: number;
    entretien: number;
    routines: number;
  };
}

const COMPOSANTES_META = [
  { cle: "nutrition" as const, label: "Nutrition", icone: Utensils, poids: "40%" },
  { cle: "budget" as const, label: "Budget", icone: Wallet, poids: "25%" },
  { cle: "entretien" as const, label: "Entretien", icone: Wrench, poids: "20%" },
  { cle: "routines" as const, label: "Routines", icone: RotateCcw, poids: "15%" },
] as const;

function couleurPourScore(score: number): string {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#f59e0b";
  return "#ef4444";
}

export function JaugeScoreFoyer({ score, composantes }: JaugeScoreFoyerProps) {
  const taille = 132;
  const scoreBorne = Math.max(0, Math.min(100, Math.round(score)));
  const stroke = 10;
  const rayon = (taille - stroke) / 2;
  const circonference = 2 * Math.PI * rayon;
  const progression = (scoreBorne / 100) * circonference;
  const couleur = couleurPourScore(scoreBorne);

  return (
    <div className="flex items-center gap-6">
      <div className="relative h-[132px] w-[132px] shrink-0">
        <svg width={taille} height={taille} className="-rotate-90">
          <circle
            cx={taille / 2}
            cy={taille / 2}
            r={rayon}
            fill="none"
            stroke="currentColor"
            strokeWidth={stroke}
            className="text-muted"
          />
          <circle
            cx={taille / 2}
            cy={taille / 2}
            r={rayon}
            fill="none"
            stroke={couleur}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circonference}
            strokeDashoffset={circonference - progression}
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Activity className="h-4 w-4 text-muted-foreground mb-0.5" />
          <p className="text-3xl font-bold leading-none">{scoreBorne}</p>
          <p className="text-xs text-muted-foreground">/100</p>
        </div>
      </div>

      <div className="space-y-1.5 text-xs text-muted-foreground flex-1">
        {COMPOSANTES_META.map(({ cle, label, icone: Icone, poids }) => {
          const val = composantes[cle];
          return (
            <div key={cle} className="flex items-center gap-1.5">
              <Icone className="h-3 w-3 shrink-0" />
              <span className="w-16">{label}</span>
              <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(100, val)}%`,
                    backgroundColor: couleurPourScore(val),
                  }}
                />
              </div>
              <span className="w-8 text-right tabular-nums">{val}%</span>
              <span className="w-8 text-[10px] opacity-60">({poids})</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
