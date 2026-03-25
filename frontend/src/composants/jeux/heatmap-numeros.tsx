"use client";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/composants/ui/tooltip";
import type { NumeroRetard } from "@/types/jeux";

interface HeatmapNumerosProps {
  frequences: Record<number, number>;
  maxNumero: number;
  colonnes?: number;
  numerosRetard?: NumeroRetard[];
  label?: string;
}

function interpolerCouleur(ratio: number): string {
  // froid (bleu) → chaud (rouge) via jaune
  if (ratio < 0.5) {
    const r = Math.round(ratio * 2 * 255);
    const g = Math.round(ratio * 2 * 200);
    return `rgb(${r}, ${g}, 255)`;
  }
  const r = 255;
  const g = Math.round((1 - (ratio - 0.5) * 2) * 200);
  return `rgb(${r}, ${g}, 50)`;
}

export function HeatmapNumeros({
  frequences,
  maxNumero,
  colonnes = 7,
  numerosRetard = [],
  label = "Fréquences",
}: HeatmapNumerosProps) {
  const vals = Object.values(frequences);
  const min = Math.min(...vals, 0);
  const max = Math.max(...vals, 1);
  const range = max - min || 1;
  const retardMap = new Map(numerosRetard.map((n) => [n.numero, n]));

  const numeros = Array.from({ length: maxNumero }, (_, i) => i + 1);

  return (
    <div className="space-y-2">
      <p className="text-sm font-semibold">{label}</p>
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${colonnes}, minmax(0, 1fr))` }}
      >
        {numeros.map((n) => {
          const freq = frequences[n] ?? 0;
          const ratio = (freq - min) / range;
          const retard = retardMap.get(n);

          return (
            <Tooltip key={n}>
              <TooltipTrigger asChild>
                <div
                  className="flex items-center justify-center rounded text-xs font-bold h-9 w-full cursor-default transition-transform hover:scale-110"
                  style={{
                    backgroundColor: interpolerCouleur(ratio),
                    color: ratio > 0.6 ? "white" : "black",
                  }}
                >
                  {n}
                  {retard && retard.value >= 2.0 && (
                    <span className="text-[8px] absolute -top-1 -right-0.5">🔥</span>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent side="top" className="text-xs">
                <p>N° {n} — fréquence : {(freq * 100).toFixed(1)}%</p>
                {retard && (
                  <>
                    <p>Série retard : {retard.serie_actuelle}</p>
                    <p>Value : {retard.value.toFixed(2)}</p>
                  </>
                )}
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>
      <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
        <div className="flex items-center gap-0.5">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: interpolerCouleur(0) }} />
          Froid
        </div>
        <div className="flex items-center gap-0.5">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: interpolerCouleur(0.5) }} />
          Moyen
        </div>
        <div className="flex items-center gap-0.5">
          <div className="h-3 w-3 rounded" style={{ backgroundColor: interpolerCouleur(1) }} />
          Chaud
        </div>
      </div>
    </div>
  );
}
