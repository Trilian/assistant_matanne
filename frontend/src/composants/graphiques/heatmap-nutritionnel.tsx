// ═══════════════════════════════════════════════════════════
// Heatmap Nutritionnel — Vue calendrier style GitHub contributions
// Rouge → Vert selon la qualité nutritionnelle de chaque jour
// ═══════════════════════════════════════════════════════════
// eslint-disable react/no-unknown-property

"use client";

import { useMemo, useState } from "react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/composants/ui/tooltip";

interface DonneeJourNutrition {
  date: string;
  score: number; // 0-100
  repas_planifies: number;
  details?: string;
}

interface HeatmapNutritionnelProps {
  donnees: DonneeJourNutrition[];
  mois?: number; // nombre de mois à afficher (défaut 3)
}

function couleurScore(score: number): string {
  if (score === 0) return "bg-muted";
  if (score < 25) return "bg-red-400 dark:bg-red-600";
  if (score < 50) return "bg-orange-400 dark:bg-orange-500";
  if (score < 75) return "bg-yellow-400 dark:bg-yellow-500";
  if (score < 90) return "bg-lime-400 dark:bg-lime-500";
  return "bg-green-500 dark:bg-green-400";
}

function obtenirSemaines(mois: number): Date[][] {
  const fin = new Date();
  const debut = new Date(fin);
  debut.setMonth(debut.getMonth() - mois);
  // Aligner au lundi
  debut.setDate(debut.getDate() - ((debut.getDay() + 6) % 7));

  const semaines: Date[][] = [];
  let semaineCourante: Date[] = [];
  const courant = new Date(debut);

  while (courant <= fin) {
    semaineCourante.push(new Date(courant));
    if (semaineCourante.length === 7) {
      semaines.push(semaineCourante);
      semaineCourante = [];
    }
    courant.setDate(courant.getDate() + 1);
  }

  if (semaineCourante.length > 0) {
    semaines.push(semaineCourante);
  }

  return semaines;
}

const JOURS_LABELS = ["L", "", "M", "", "V", "", ""];
const MOIS_LABELS = [
  "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
  "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc",
];

export function HeatmapNutritionnel({ donnees, mois = 3 }: HeatmapNutritionnelProps) {
  const donneesMap = useMemo(() => {
    const m = new Map<string, DonneeJourNutrition>();
    for (const d of donnees) {
      m.set(d.date, d);
    }
    return m;
  }, [donnees]);

  const semaines = useMemo(() => obtenirSemaines(mois), [mois]);

  // Labels des mois en haut
  const moisLabels = useMemo(() => {
    const labels: { texte: string; colonne: number }[] = [];
    let dernierMois = -1;
    semaines.forEach((semaine, i) => {
      const premier = semaine[0];
      const m = premier.getMonth();
      if (m !== dernierMois) {
        labels.push({ texte: MOIS_LABELS[m], colonne: i });
        dernierMois = m;
      }
    });
    return labels;
  }, [semaines]);

  return (
    <div className="space-y-2">
      {/* Mois labels */}
      <div className="flex gap-0.5 ml-6 text-[10px] text-muted-foreground">
        {moisLabels.map((label, i) => (
          <span
            key={i}
            // eslint-disable-next-line react/no-unknown-property
            style={{ marginLeft: i === 0 ? 0 : `${(label.colonne - (moisLabels[i - 1]?.colonne ?? 0) - 1) * 14}px` }}
          >
            {label.texte}
          </span>
        ))}
      </div>

      <div className="flex gap-1">
        {/* Jours labels */}
        <div className="flex flex-col gap-0.5 text-[10px] text-muted-foreground pr-1">
          {JOURS_LABELS.map((j, i) => (
            <div key={i} className="h-3 flex items-center">{j}</div>
          ))}
        </div>

        {/* Grille */}
        <div className="flex gap-0.5">
          {semaines.map((semaine, si) => (
            <div key={si} className="flex flex-col gap-0.5">
              {semaine.map((jour) => {
                const cle = jour.toISOString().split("T")[0];
                const data = donneesMap.get(cle);
                const score = data?.score ?? 0;
                const aData = !!data;

                return (
                  <Tooltip key={cle}>
                    <TooltipTrigger asChild>
                      <div
                        className={`h-3 w-3 rounded-[2px] transition-colors ${
                          aData ? couleurScore(score) : "bg-muted/50"
                        }`}
                      />
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs">
                      <p className="font-medium">
                        {jour.toLocaleDateString("fr-FR", {
                          weekday: "short",
                          day: "numeric",
                          month: "short",
                        })}
                      </p>
                      {aData ? (
                        <>
                          <p>Score: {score}/100</p>
                          <p>{data.repas_planifies} repas planifié(s)</p>
                          {data.details && <p className="text-muted-foreground">{data.details}</p>}
                        </>
                      ) : (
                        <p className="text-muted-foreground">Aucune donnée</p>
                      )}
                    </TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Légende */}
      <div className="flex items-center gap-1 text-[10px] text-muted-foreground mt-1">
        <span>Faible</span>
        <div className="h-3 w-3 rounded-[2px] bg-red-400" />
        <div className="h-3 w-3 rounded-[2px] bg-orange-400" />
        <div className="h-3 w-3 rounded-[2px] bg-yellow-400" />
        <div className="h-3 w-3 rounded-[2px] bg-lime-400" />
        <div className="h-3 w-3 rounded-[2px] bg-green-500" />
        <span>Excellent</span>
      </div>
    </div>
  );
}
