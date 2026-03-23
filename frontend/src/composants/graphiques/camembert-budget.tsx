"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const COULEURS = [
  "hsl(210, 70%, 50%)",
  "hsl(340, 70%, 50%)",
  "hsl(150, 60%, 40%)",
  "hsl(40, 80%, 50%)",
  "hsl(270, 60%, 55%)",
  "hsl(20, 75%, 50%)",
  "hsl(180, 55%, 45%)",
  "hsl(0, 65%, 50%)",
];

interface DonneeCategorie {
  nom: string;
  montant: number;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function renderLabel(entry: any) {
  const name = entry.nom ?? entry.name ?? "";
  const pct = typeof entry.percent === "number" ? (entry.percent * 100).toFixed(0) : "0";
  return `${name} ${pct}%`;
}

export function CamembertBudget({ donnees }: { donnees: DonneeCategorie[] }) {
  if (!donnees.length) return null;

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={donnees}
          dataKey="montant"
          nameKey="nom"
          cx="50%"
          cy="50%"
          outerRadius={80}
          innerRadius={40}
          paddingAngle={2}
          label={renderLabel}
          labelLine={false}
        >
          {donnees.map((_, i) => (
            <Cell key={i} fill={COULEURS[i % COULEURS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value) => `${Number(value).toFixed(2)} €`}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
