"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { COULEURS_GRAPHIQUES } from "@/bibliotheque/theme-graphiques";

const COULEURS_CATEGORIES: Record<string, string> = {
  motricite: COULEURS_GRAPHIQUES.accent2,
  langage: COULEURS_GRAPHIQUES.accent4,
  cognitif: COULEURS_GRAPHIQUES.accent5,
  social: COULEURS_GRAPHIQUES.accent1,
  autre: COULEURS_GRAPHIQUES.accent3,
};

interface DonneeJalon {
  categorie: string;
  label: string;
  nombre: number;
}

export function GraphiqueJalons({ donnees }: { donnees: DonneeJalon[] }) {
  if (!donnees.length) return null;

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={donnees} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip
          formatter={(value) => [`${value} jalons`, "Nombre"]}
        />
        <Bar dataKey="nombre" radius={[4, 4, 0, 0]}>
          {donnees.map((d, i) => (
            <Cell
              key={i}
              fill={COULEURS_CATEGORIES[d.categorie] ?? COULEURS_GRAPHIQUES.muted}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
