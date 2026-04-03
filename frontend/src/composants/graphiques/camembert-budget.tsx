"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { PALETTE_GRAPHIQUES } from "@/bibliotheque/theme-graphiques";

const COULEURS = PALETTE_GRAPHIQUES;

interface DonneeCategorie {
  nom: string;
  montant: number;
}

interface LabelEntry {
  nom?: string;
  name?: string;
  percent?: number;
}

function renderLabel(entry: LabelEntry) {
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
