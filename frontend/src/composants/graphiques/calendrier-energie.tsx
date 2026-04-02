"use client";

import { useMemo } from "react";

interface ReleveCalendrier {
  id: number;
  date_releve: string;
  valeur: number;
}

function couleurCellule(valeur: number, max: number) {
  if (valeur <= 0 || max <= 0) return "bg-muted text-muted-foreground";
  const ratio = valeur / max;
  if (ratio >= 0.85) return "bg-red-500/85 text-white";
  if (ratio >= 0.65) return "bg-orange-400/85 text-orange-950";
  if (ratio >= 0.4) return "bg-amber-300/85 text-amber-950";
  return "bg-emerald-300/85 text-emerald-950";
}

export function CalendrierEnergie({
  releves,
}: {
  releves: ReleveCalendrier[];
}) {
  const donnees = useMemo(() => {
    const maintenant = new Date();
    const annee = maintenant.getFullYear();
    const mois = maintenant.getMonth();
    const debut = new Date(annee, mois, 1);
    const fin = new Date(annee, mois + 1, 0);
    const premierJour = (debut.getDay() + 6) % 7;
    const joursDansMois = fin.getDate();

    const parJour = new Map(
      releves.map((releve) => [releve.date_releve.slice(0, 10), releve.valeur])
    );

    const cellules: Array<{ cle: string; jour?: number; valeur?: number }> = [];
    for (let index = 0; index < premierJour; index += 1) {
      cellules.push({ cle: `vide-${index}` });
    }

    for (let jour = 1; jour <= joursDansMois; jour += 1) {
      const date = new Date(annee, mois, jour).toISOString().slice(0, 10);
      cellules.push({
        cle: date,
        jour,
        valeur: parJour.get(date),
      });
    }

    const max = Math.max(...cellules.map((cellule) => cellule.valeur ?? 0), 0);
    return { cellules, max, label: debut.toLocaleDateString("fr-FR", { month: "long", year: "numeric" }) };
  }, [releves]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium capitalize">{donnees.label}</span>
        <span className="text-muted-foreground">Lecture colorée par relevé disponible</span>
      </div>
      <div className="grid grid-cols-7 gap-2 text-center text-xs text-muted-foreground">
        {["L", "M", "M", "J", "V", "S", "D"].map((jour) => (
          <div key={jour}>{jour}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-2">
        {donnees.cellules.map((cellule) => (
          <div
            key={cellule.cle}
            className={`flex aspect-square flex-col items-center justify-center rounded-xl border text-xs ${
              cellule.jour ? couleurCellule(cellule.valeur ?? 0, donnees.max) : "border-dashed border-transparent"
            }`}
            title={
              cellule.jour
                ? `${cellule.jour}: ${cellule.valeur != null ? `${cellule.valeur} relevé` : "aucune lecture"}`
                : undefined
            }
          >
            {cellule.jour ? (
              <>
                <span className="font-medium">{cellule.jour}</span>
                <span className="text-[10px] opacity-80">{cellule.valeur != null ? Math.round(cellule.valeur) : "-"}</span>
              </>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}
