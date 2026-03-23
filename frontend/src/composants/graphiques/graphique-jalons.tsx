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

const COULEURS_CATEGORIES: Record<string, string> = {
  motricite: "hsl(210, 70%, 50%)",
  langage: "hsl(340, 70%, 50%)",
  cognitif: "hsl(270, 60%, 55%)",
  social: "hsl(150, 60%, 40%)",
  autre: "hsl(40, 80%, 50%)",
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
              fill={COULEURS_CATEGORIES[d.categorie] ?? "hsl(210, 10%, 60%)"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
