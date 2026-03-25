// ═══════════════════════════════════════════════════════════
// Carte Tâche du Jour — avec timer optionnel
// ═══════════════════════════════════════════════════════════

"use client";

import { CheckCircle2, Clock, Circle } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import type { TacheJourMaison } from "@/types/maison";

interface CarteTacheJourProps {
  tache: TacheJourMaison;
  onToggle?: (idSource: number, fait: boolean) => void;
}

function prioriteBadge(priorite?: string) {
  if (!priorite) return null;
  const variant =
    priorite === "CRITIQUE" || priorite === "HAUTE"
      ? ("destructive" as const)
      : priorite === "MOYENNE"
        ? ("secondary" as const)
        : ("outline" as const);
  return <Badge variant={variant} className="text-xs">{priorite}</Badge>;
}

export function CarteTacheJour({ tache, onToggle }: CarteTacheJourProps) {
  const handleToggle = () => {
    if (tache.id_source && onToggle) {
      onToggle(tache.id_source, !tache.fait);
    }
  };

  return (
    <div className="flex items-center gap-3 py-2">
      <Button
        variant="ghost"
        size="icon"
        className="h-6 w-6 shrink-0"
        onClick={handleToggle}
        disabled={!tache.id_source || !onToggle}
        aria-label={tache.fait ? "Marquer non fait" : "Marquer fait"}
      >
        {tache.fait
          ? <CheckCircle2 className="h-5 w-5 text-green-500" />
          : <Circle className="h-5 w-5 text-muted-foreground" />
        }
      </Button>

      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium leading-tight ${tache.fait ? "line-through text-muted-foreground" : ""}`}>
          {tache.nom}
        </p>
        {tache.categorie && (
          <p className="text-xs text-muted-foreground">{tache.categorie}</p>
        )}
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        {prioriteBadge(tache.priorite)}
        {tache.duree_estimee_min && (
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {tache.duree_estimee_min} min
          </span>
        )}
      </div>
    </div>
  );
}
