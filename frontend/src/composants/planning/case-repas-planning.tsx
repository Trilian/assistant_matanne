// ═══════════════════════════════════════════════════════════
// CaseRepasPlanning — cellule droppable d'un type de repas/date
// ═══════════════════════════════════════════════════════════

"use client";

import { Plus } from "lucide-react";
import { useDroppable } from "@dnd-kit/core";
import { Button } from "@/composants/ui/button";
import { CarteRepasDraggable } from "./carte-repas-draggable";
import type { TypeRepas, RepasPlanning } from "@/types/planning";

export function construireIdCasePlanning(date: string, type: TypeRepas): string {
  return `case::${date}::${type}`;
}

export function CaseRepasPlanning({
  date,
  type,
  label,
  emoji,
  repas,
  repasGlisse,
  onAjouter,
  onRetirer,
  onModifierChamp,
  onRegenerer,
  nomDinerParDescription,
}: {
  date: string;
  type: TypeRepas;
  label: string;
  emoji: string;
  repas?: RepasPlanning;
  repasGlisse: RepasPlanning | null;
  onAjouter: (date: string, type: TypeRepas) => void;
  onRetirer: (repas: RepasPlanning) => void;
  onModifierChamp?: (repasId: number, champ: string, valeur: string) => void;
  onRegenerer?: (repas: RepasPlanning) => void;
  nomDinerParDescription: Record<string, string>;
}) {
  const { isOver, setNodeRef } = useDroppable({
    id: construireIdCasePlanning(date, type),
    data: { date, type },
  });

  const dateSource = (repasGlisse?.date_repas || repasGlisse?.date || "").split("T")[0];
  const estCibleDrop =
    Boolean(repasGlisse) && !(dateSource === date && repasGlisse?.type_repas === type);

  return (
    <div
      ref={setNodeRef}
      className={`min-h-[48px] rounded-md border border-dashed p-2 text-xs transition-colors ${
        isOver || estCibleDrop
          ? "border-primary/50 bg-primary/5"
          : "border-muted-foreground/25"
      }`}
    >
      <div className="text-muted-foreground mb-1">
        {emoji} {label}
      </div>
      {repas ? (
        <CarteRepasDraggable
          repas={repas}
          label={label}
          onRetirer={onRetirer}
          onModifierChamp={onModifierChamp}
          onRegenerer={onRegenerer}
          nomDinerSource={
            repas.est_reste && repas.reste_description
              ? nomDinerParDescription[repas.reste_description]
              : undefined
          }
        />
      ) : (
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-full text-xs"
          onClick={() => onAjouter(date, type)}
        >
          <Plus className="h-3 w-3 mr-1" />
          Ajouter
        </Button>
      )}
    </div>
  );
}
