"use client";

import { useMemo, useState } from "react";
import { ArrowLeft } from "lucide-react";

import { Button } from "@/composants/ui/button";
import { cn } from "@/bibliotheque/utils";

export interface DonneeInventaireTreemap {
  nom: string;
  quantite: number;
  couleur?: string;
  sous_categories?: DonneeInventaireTreemap[];
}

interface TreemapInventaireProps {
  donnees: DonneeInventaireTreemap[];
  hauteur?: number;
}

interface RectTreemap {
  x: number;
  y: number;
  w: number;
  h: number;
  donnee: DonneeInventaireTreemap;
  couleur: string;
}

const COULEURS = [
  "hsl(161, 64%, 42%)",
  "hsl(213, 80%, 52%)",
  "hsl(29, 94%, 52%)",
  "hsl(342, 75%, 48%)",
  "hsl(264, 65%, 56%)",
  "hsl(190, 68%, 42%)",
  "hsl(84, 63%, 38%)",
  "hsl(8, 76%, 55%)",
];

function calculerTreemap(
  donnees: DonneeInventaireTreemap[],
  x: number,
  y: number,
  w: number,
  h: number
): RectTreemap[] {
  if (!donnees.length) return [];

  const total = donnees.reduce((somme, item) => somme + item.quantite, 0);
  if (total <= 0) return [];

  const tries = [...donnees].sort((a, b) => b.quantite - a.quantite);
  const rects: RectTreemap[] = [];

  let courantX = x;
  let courantY = y;
  let courantW = w;
  let courantH = h;
  let restant = total;

  tries.forEach((item, index) => {
    const ratio = item.quantite / restant;
    const couleur = item.couleur ?? COULEURS[index % COULEURS.length];
    const horizontal = courantW >= courantH;

    if (horizontal) {
      const largeur = courantW * ratio;
      rects.push({ x: courantX, y: courantY, w: largeur, h: courantH, donnee: item, couleur });
      courantX += largeur;
      courantW -= largeur;
    } else {
      const hauteur = courantH * ratio;
      rects.push({ x: courantX, y: courantY, w: courantW, h: hauteur, donnee: item, couleur });
      courantY += hauteur;
      courantH -= hauteur;
    }

    restant -= item.quantite;
  });

  return rects;
}

export function TreemapInventaire({ donnees, hauteur = 320 }: TreemapInventaireProps) {
  const [selection, setSelection] = useState<DonneeInventaireTreemap | null>(null);
  const donneesActuelles = selection?.sous_categories ?? donnees;
  const total = donneesActuelles.reduce((somme, item) => somme + item.quantite, 0);
  const classeHauteur =
    hauteur === 260
      ? "h-[260px]"
      : hauteur === 280
        ? "h-[280px]"
        : hauteur === 300
          ? "h-[300px]"
          : "h-[320px]";

  const rects = useMemo(
    () => calculerTreemap(donneesActuelles, 0, 0, 100, 100),
    [donneesActuelles]
  );

  if (!donnees.length || total <= 0) {
    return (
      <div className="flex h-[320px] items-center justify-center text-sm text-muted-foreground">
        Aucune donnee d&apos;inventaire exploitable.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {selection ? (
        <Button variant="ghost" size="sm" className="-ml-2 gap-1" onClick={() => setSelection(null)}>
          <ArrowLeft className="h-3 w-3" />
          Retour
        </Button>
      ) : null}

      <div className={cn("overflow-hidden rounded-lg border", classeHauteur)}>
        <svg viewBox="0 0 100 100" className="h-full w-full" preserveAspectRatio="none">
          {rects.map((rect) => {
            const pourcentage = ((rect.donnee.quantite / total) * 100).toFixed(0);
            const estPetit = rect.w < 12 || rect.h < 12;
            const aEnfants = (rect.donnee.sous_categories?.length ?? 0) > 0;

            return (
              <g
                key={rect.donnee.nom}
                className={aEnfants ? "cursor-pointer" : undefined}
                onClick={() => {
                  if (aEnfants) setSelection(rect.donnee);
                }}
              >
                <rect
                  x={rect.x}
                  y={rect.y}
                  width={rect.w}
                  height={rect.h}
                  fill={rect.couleur}
                  stroke="rgba(255,255,255,0.25)"
                  strokeWidth={0.35}
                />
                {estPetit ? null : (
                  <>
                    <text
                      x={rect.x + rect.w / 2}
                      y={rect.y + rect.h / 2 - 2}
                      textAnchor="middle"
                      className="fill-white text-[3.2px] font-semibold"
                    >
                      {rect.donnee.nom}
                    </text>
                    <text
                      x={rect.x + rect.w / 2}
                      y={rect.y + rect.h / 2 + 3}
                      textAnchor="middle"
                      className="fill-white/90 text-[2.5px]"
                    >
                      {rect.donnee.quantite.toFixed(0)} u ({pourcentage}%)
                    </text>
                  </>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {selection ? (
        <p className="text-xs text-muted-foreground">
          Drill-down : <strong>{selection.nom}</strong> - {selection.quantite.toFixed(0)} unites
        </p>
      ) : null}
    </div>
  );
}
