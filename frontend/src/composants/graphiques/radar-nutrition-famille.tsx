"use client";

import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

const OBJECTIFS_JOUR = {
  calories: 2000,
  proteines: 60,
  lipides: 70,
  glucides: 260,
};

export function RadarNutritionFamille({
  totaux,
  nbJours,
}: {
  totaux: { calories: number; proteines: number; lipides: number; glucides: number };
  nbJours: number;
}) {
  const data = [
    {
      label: "Calories",
      famille: Math.round(totaux.calories / Math.max(1, nbJours)),
      cible: OBJECTIFS_JOUR.calories,
    },
    {
      label: "Protéines",
      famille: Math.round(totaux.proteines / Math.max(1, nbJours)),
      cible: OBJECTIFS_JOUR.proteines,
    },
    {
      label: "Lipides",
      famille: Math.round(totaux.lipides / Math.max(1, nbJours)),
      cible: OBJECTIFS_JOUR.lipides,
    },
    {
      label: "Glucides",
      famille: Math.round(totaux.glucides / Math.max(1, nbJours)),
      cible: OBJECTIFS_JOUR.glucides,
    },
  ];

  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} outerRadius="72%">
        <PolarGrid stroke="hsl(0 0% 82%)" />
        <PolarAngleAxis dataKey="label" tick={{ fontSize: 12 }} />
        <PolarRadiusAxis tick={{ fontSize: 10 }} />
        <Radar
          dataKey="famille"
          name="Réalisé"
          stroke="hsl(160 84% 32%)"
          fill="hsl(160 84% 32%)"
          fillOpacity={0.28}
          strokeWidth={2}
        />
        <Radar
          dataKey="cible"
          name="Objectif"
          stroke="hsl(215 90% 55%)"
          fill="hsl(215 90% 55%)"
          fillOpacity={0.08}
          strokeWidth={2}
          strokeDasharray="5 5"
        />
        <Tooltip formatter={(value, name) => [`${value}`, String(name)]} />
        <Legend wrapperStyle={{ fontSize: "12px" }} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
