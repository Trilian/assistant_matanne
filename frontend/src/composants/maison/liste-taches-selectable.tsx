// ═══════════════════════════════════════════════════════════
// ListeTachesSelectable — Sélection de tâches avec cases à cocher
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Card, CardContent } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Checkbox } from "@/composants/ui/checkbox";

type Tache = {
  nom: string;
  duree_estimee_min?: number;
  categorie?: string;
};

interface ListeTachesSelectableProps {
  taches: Tache[];
  onValider: (tachesSelectionnees: Tache[]) => void;
  labelBouton?: string;
  isLoading?: boolean;
}

export function ListeTachesSelectable({
  taches,
  onValider,
  labelBouton = "Valider la sélection",
  isLoading = false,
}: ListeTachesSelectableProps) {
  const [selectionnees, setSelectionnees] = useState<Set<number>>(new Set());

  const toutSelectionner = () => {
    setSelectionnees(new Set(taches.map((_, i) => i)));
  };

  const toutDeselectionner = () => {
    setSelectionnees(new Set());
  };

  const basculer = (index: number) => {
    setSelectionnees((prev) => {
      const suivant = new Set(prev);
      if (suivant.has(index)) {
        suivant.delete(index);
      } else {
        suivant.add(index);
      }
      return suivant;
    });
  };

  const toutesSelectionnees = selectionnees.size === taches.length && taches.length > 0;

  const handleValider = () => {
    const tachesSelectionnees = taches.filter((_, i) => selectionnees.has(i));
    onValider(tachesSelectionnees);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">
          {selectionnees.size} / {taches.length} tâche{taches.length !== 1 ? "s" : ""} sélectionnée{selectionnees.size !== 1 ? "s" : ""}
        </span>
        <Button
          variant="ghost"
          size="sm"
          className="text-xs h-7"
          onClick={toutesSelectionnees ? toutDeselectionner : toutSelectionner}
        >
          {toutesSelectionnees ? "Tout désélectionner" : "Tout sélectionner"}
        </Button>
      </div>

      <div className="space-y-2">
        {taches.map((tache, index) => (
          <Card
            key={index}
            className={`cursor-pointer transition-colors ${selectionnees.has(index) ? "border-primary bg-primary/5" : ""}`}
            onClick={() => basculer(index)}
          >
            <CardContent className="flex items-center gap-3 py-2.5 px-3">
              <Checkbox
                checked={selectionnees.has(index)}
                onCheckedChange={() => basculer(index)}
                onClick={(e) => e.stopPropagation()}
              />
              <span className="flex-1 text-sm font-medium">{tache.nom}</span>
              <div className="flex items-center gap-1.5">
                {tache.duree_estimee_min && (
                  <Badge variant="outline" className="text-xs">
                    {tache.duree_estimee_min} min
                  </Badge>
                )}
                {tache.categorie && (
                  <Badge variant="secondary" className="text-xs capitalize">
                    {tache.categorie}
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Button
        onClick={handleValider}
        disabled={selectionnees.size === 0 || isLoading}
        className="w-full"
      >
        {isLoading ? "Chargement..." : labelBouton}
      </Button>
    </div>
  );
}
