// ═══════════════════════════════════════════════════════════
// Radar Skill Jules — Motricité, Langage, Social, Cognitif vs normes OMS
// Superposition du profil Jules et de la moyenne OMS
// ═══════════════════════════════════════════════════════════

"use client";

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { COULEURS_GRAPHIQUES } from "@/bibliotheque/theme-graphiques";

interface DonneeRadarJules {
  categorie: string;
  label: string;
  jules: number; // score 0-100
  norme_oms: number; // score 0-100 (moyenne OMS pour l'âge)
}

interface RadarSkillJulesProps {
  donnees: DonneeRadarJules[];
  ageMois?: number;
}

export function RadarSkillJules({ donnees, ageMois }: RadarSkillJulesProps) {
  if (donnees.length < 3) {
    return (
      <div className="flex items-center justify-center h-[250px] text-muted-foreground text-sm">
        Ajoutez plus de jalons (3 catégories minimum) pour voir le radar.
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {ageMois && (
        <p className="text-xs text-muted-foreground text-center">
          Comparaison à {ageMois} mois — Normes OMS
        </p>
      )}
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={donnees}>
          <PolarGrid stroke={COULEURS_GRAPHIQUES.grille} />
          <PolarAngleAxis
            dataKey="label"
            tick={{ fontSize: 12, fill: COULEURS_GRAPHIQUES.muted }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 10 }}
            tickCount={5}
          />
          <Radar
            name="Jules"
            dataKey="jules"
            stroke={COULEURS_GRAPHIQUES.accent2}
            fill={COULEURS_GRAPHIQUES.accent2}
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Radar
            name="Norme OMS"
            dataKey="norme_oms"
            stroke={COULEURS_GRAPHIQUES.accent1}
            fill={COULEURS_GRAPHIQUES.accent1}
            fillOpacity={0.1}
            strokeWidth={1.5}
            strokeDasharray="5 5"
          />
          <Tooltip
            formatter={(value, name) => [
              `${typeof value === "number" ? value : String(value ?? "")}/100`,
              String(name ?? ""),
            ]}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
