// ═══════════════════════════════════════════════════════════
// Treemap Budget — Vue proportionnelle des dépenses par catégorie
// Cliquable avec drill-down (sous-catégories)
// ═══════════════════════════════════════════════════════════

"use client";

import { useMemo, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { cn } from "@/bibliotheque/utils";

export interface DonneeCategorieTreemap {
  nom: string;
  montant: number;
  couleur?: string;
  sous_categories?: DonneeCategorieTreemap[];
}

interface TreemapBudgetProps {
  donnees: DonneeCategorieTreemap[];
  hauteur?: number;
}

const COULEURS = [
  "hsl(210, 70%, 50%)",
  "hsl(340, 70%, 50%)",
  "hsl(150, 60%, 40%)",
  "hsl(40, 80%, 50%)",
  "hsl(270, 60%, 55%)",
  "hsl(20, 75%, 50%)",
  "hsl(180, 55%, 45%)",
  "hsl(0, 65%, 50%)",
  "hsl(120, 50%, 45%)",
  "hsl(300, 50%, 50%)",
];

interface RectTreemap {
  x: number;
  y: number;
  w: number;
  h: number;
  donnee: DonneeCategorieTreemap;
  couleur: string;
}

function calculerTreemap(
  donnees: DonneeCategorieTreemap[],
  x: number,
  y: number,
  w: number,
  h: number
): RectTreemap[] {
  if (donnees.length === 0) return [];

  const total = donnees.reduce((s, d) => s + d.montant, 0);
  if (total === 0) return [];

  const tries = [...donnees].sort((a, b) => b.montant - a.montant);
  const rects: RectTreemap[] = [];

  let cx = x, cy = y, cw = w, ch = h;
  let restant = total;

  tries.forEach((d, i) => {
    const ratio = d.montant / restant;
    const couleur = d.couleur ?? COULEURS[i % COULEURS.length];
    const horizontal = cw >= ch;

    if (horizontal) {
      const rw = cw * ratio;
      rects.push({ x: cx, y: cy, w: rw, h: ch, donnee: d, couleur });
      cx += rw;
      cw -= rw;
    } else {
      const rh = ch * ratio;
      rects.push({ x: cx, y: cy, w: cw, h: rh, donnee: d, couleur });
      cy += rh;
      ch -= rh;
    }

    restant -= d.montant;
  });

  return rects;
}

export function TreemapBudget({ donnees, hauteur = 300 }: TreemapBudgetProps) {
  const [selection, setSelection] = useState<DonneeCategorieTreemap | null>(null);
  const donneesActuelles = selection?.sous_categories ?? donnees;
  const total = donneesActuelles.reduce((s, d) => s + d.montant, 0);

  const rects = useMemo(
    () => calculerTreemap(donneesActuelles, 0, 0, 100, 100),
    [donneesActuelles]
  );

  if (!donnees.length || total === 0) {
    return (
      <div className="flex items-center justify-center text-muted-foreground text-sm" style={{ height: hauteur }}>
        Aucune donnée de budget
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {selection && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSelection(null)}
          className="gap-1 -ml-2"
        >
          <ArrowLeft className="h-3 w-3" />
          Retour
        </Button>
      )}
      <div
        className="relative rounded-lg overflow-hidden border"
        style={{ height: hauteur }}
      >
        {rects.map((rect) => {
          const pct = ((rect.donnee.montant / total) * 100).toFixed(0);
          const estTropPetit = rect.w < 12 || rect.h < 12;
          const aEnfants = (rect.donnee.sous_categories?.length ?? 0) > 0;

          return (
            <button
              key={rect.donnee.nom}
              type="button"
              className={cn(
                "absolute transition-all duration-300 flex flex-col items-center justify-center text-white",
                "border border-white/20",
                aEnfants ? "cursor-pointer hover:brightness-110" : "cursor-default"
              )}
              style={{
                left: `${rect.x}%`,
                top: `${rect.y}%`,
                width: `${rect.w}%`,
                height: `${rect.h}%`,
                backgroundColor: rect.couleur,
              }}
              onClick={() => {
                if (aEnfants) setSelection(rect.donnee);
              }}
            >
              {!estTropPetit && (
                <>
                  <span className="text-xs font-semibold truncate max-w-full px-1">
                    {rect.donnee.nom}
                  </span>
                  <span className="text-[10px] opacity-80">
                    {rect.donnee.montant.toFixed(0)} € ({pct}%)
                  </span>
                </>
              )}
            </button>
          );
        })}
      </div>
      {selection && (
        <p className="text-xs text-muted-foreground">
          Drill-down : <strong>{selection.nom}</strong> — {selection.montant.toFixed(0)} € total
        </p>
      )}
    </div>
  );
}
