// ═══════════════════════════════════════════════════════════
// CarteRoutine — Carte d'une routine avec tâches et progression
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";

const COULEUR_CATEGORIE: Record<string, string> = {
  quotidien: "bg-amber-100 text-amber-800",
  hebdomadaire: "bg-green-100 text-green-800",
  mensuel: "bg-purple-100 text-purple-800",
};

const ICONE_MOMENT: Record<string, string> = {
  matin: "🌅",
  apres_midi: "☀️",
  soir: "🌙",
  flexible: "🕐",
};

export interface TacheRoutineItem {
  nom: string;
  duree_min: number;
  ordre: number;
  categorie?: string;
}

export interface RoutineData {
  id?: number;
  nom: string;
  frequence: string;
  categorie: string;
  moment_journee?: string;
  heure_debut?: string;
  heure_fin?: string;
  taches: TacheRoutineItem[];
}

interface CarteRoutineProps {
  routine: RoutineData;
  tachesOk?: string[];
  onToggleTache?: (routineId: string, tacheNom: string) => void;
  className?: string;
}

export function CarteRoutine({
  routine,
  tachesOk = [],
  onToggleTache,
  className,
}: CarteRoutineProps) {
  const [ouvert, setOuvert] = useState(false);

  const tachesTriees = [...routine.taches].sort((a, b) => a.ordre - b.ordre);
  const total = tachesTriees.length;
  const faites = tachesTriees.filter((t) => tachesOk.includes(t.nom)).length;
  const pourcentage = total > 0 ? Math.round((faites / total) * 100) : 0;
  const dureeTotal = tachesTriees.reduce((acc, t) => acc + t.duree_min, 0);
  const routineId = String(routine.id ?? routine.nom);

  return (
    <Card className={`transition-shadow hover:shadow-md ${className ?? ""}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <span className="text-lg">
              {ICONE_MOMENT[routine.moment_journee ?? "flexible"]}
            </span>
            <div className="min-w-0">
              <p className="font-semibold text-sm truncate">{routine.nom}</p>
              <div className="flex items-center gap-1 mt-0.5 flex-wrap">
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                    COULEUR_CATEGORIE[routine.categorie] ?? "bg-muted text-muted-foreground"
                  }`}
                >
                  {routine.frequence}
                </span>
                {routine.heure_debut && (
                  <span className="text-xs text-muted-foreground">
                    {routine.heure_debut}
                    {routine.heure_fin && `–${routine.heure_fin}`}
                  </span>
                )}
                <span className="text-xs text-muted-foreground">⏱ {dureeTotal} min</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            {total > 0 && (
              <Badge
                variant={pourcentage === 100 ? "default" : "outline"}
                className="text-xs"
              >
                {faites}/{total}
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-muted-foreground"
              onClick={() => setOuvert(!ouvert)}
            >
              {ouvert ? "▲" : "▼"}
            </Button>
          </div>
        </div>

        {/* Barre de progression */}
        {total > 0 && (
          <div className="mt-2 space-y-1">
            <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
              <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pourcentage}%` }} />
            </div>
            {pourcentage === 100 && (
              <p className="text-xs text-green-600 font-medium">✓ Routine complète !</p>
            )}
          </div>
        )}
      </CardHeader>

      {/* Tâches dépliables */}
      {ouvert && (
        <CardContent className="pt-0">
          <div className="space-y-2 mt-2">
            {tachesTriees.map((tache, i) => {
              const estFaite = tachesOk.includes(tache.nom);
              return (
                <div
                  key={i}
                  className={`flex items-center gap-3 rounded-md p-2 transition-opacity ${
                    estFaite ? "opacity-50" : "hover:bg-muted/50"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={estFaite}
                    onChange={() => onToggleTache?.(routineId, tache.nom)}
                    id={`${routineId}-${i}`}
                    disabled={!onToggleTache}
                    className="h-4 w-4 rounded border-border cursor-pointer disabled:cursor-not-allowed"
                  />
                  <label
                    htmlFor={`${routineId}-${i}`}
                    className={`flex-1 text-sm cursor-pointer ${
                      estFaite ? "line-through text-muted-foreground" : ""
                    }`}
                  >
                    {tache.nom}
                  </label>
                  <span className="text-xs text-muted-foreground">{tache.duree_min}m</span>
                </div>
              );
            })}
          </div>
        </CardContent>
      )}
    </Card>
  );
}
