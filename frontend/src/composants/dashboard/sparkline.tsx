// ═══════════════════════════════════════════════════════════
// Sparkline — Mini graphique tendance 7 jours pour les cartes
// ═══════════════════════════════════════════════════════════

"use client";

import { useMemo } from "react";
import { motion } from "framer-motion";

interface SparklineProps {
  donnees: number[];
  largeur?: number;
  hauteur?: number;
  couleur?: string;
  couleurNegatif?: string;
  remplissage?: boolean;
}

export function Sparkline({
  donnees,
  largeur = 80,
  hauteur = 24,
  couleur = "currentColor",
  couleurNegatif,
  remplissage = true,
}: SparklineProps) {
  const chemin = useMemo(() => {
    if (donnees.length < 2) return "";

    const min = Math.min(...donnees);
    const max = Math.max(...donnees);
    const plage = max - min || 1;
    const padding = 2;
    const w = largeur - padding * 2;
    const h = hauteur - padding * 2;

    const points = donnees.map((v, i) => ({
      x: padding + (i / (donnees.length - 1)) * w,
      y: padding + h - ((v - min) / plage) * h,
    }));

    const ligne = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
      .join(" ");

    return ligne;
  }, [donnees, largeur, hauteur]);

  const cheminRemplissage = useMemo(() => {
    if (!remplissage || donnees.length < 2) return "";
    const min = Math.min(...donnees);
    const max = Math.max(...donnees);
    const plage = max - min || 1;
    const padding = 2;
    const w = largeur - padding * 2;
    const h = hauteur - padding * 2;

    const points = donnees.map((v, i) => ({
      x: padding + (i / (donnees.length - 1)) * w,
      y: padding + h - ((v - min) / plage) * h,
    }));

    const ligne = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
      .join(" ");

    return `${ligne} L ${points[points.length - 1].x.toFixed(1)} ${hauteur} L ${points[0].x.toFixed(1)} ${hauteur} Z`;
  }, [donnees, largeur, hauteur, remplissage]);

  if (donnees.length < 2) return null;

  const tendance = donnees[donnees.length - 1] - donnees[0];
  const couleurEffective =
    couleurNegatif && tendance < 0 ? couleurNegatif : couleur;

  return (
    <svg
      width={largeur}
      height={hauteur}
      viewBox={`0 0 ${largeur} ${hauteur}`}
      className="inline-block"
    >
      {remplissage && cheminRemplissage && (
        <motion.path
          d={cheminRemplissage}
          fill={couleurEffective}
          opacity={0.1}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.14 }}
          transition={{ duration: 0.45, ease: "easeOut" }}
        />
      )}
      <motion.path
        d={chemin}
        fill="none"
        stroke={couleurEffective}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.65, ease: "easeOut" }}
      />
    </svg>
  );
}
