'use client'

import { GripVertical } from "lucide-react";
import {
  closestCenter,
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { Badge } from "@/composants/ui/badge";
import { CalendrierMensuel } from "@/composants/planning/calendrier-mensuel";
import { CaseRepasPlanning } from "@/composants/planning/case-repas-planning";
import type { TypeRepas, RepasPlanning } from "@/types/planning";

// ─── Constantes exportées (réutilisées par page.tsx) ───
export const STAGGER_DELAYS = [
  "delay-0",
  "delay-75",
  "delay-150",
  "delay-200",
  "delay-300",
  "delay-500",
  "delay-700",
];

export const TYPES_REPAS: { valeur: TypeRepas; label: string; emoji: string }[] = [
  { valeur: "petit_dejeuner", label: "Petit-déj", emoji: "🌅" },
  { valeur: "dejeuner", label: "Déjeuner", emoji: "☀️" },
  { valeur: "gouter", label: "Goûter", emoji: "🍪" },
  { valeur: "diner", label: "Dîner", emoji: "🌙" },
];

interface GrillePlanningHebdoProps {
  modeAffichage: string;
  chargementMensuel: boolean;
  planningMensuel: { mois: string; par_jour: Record<string, RepasPlanning[]> } | null | undefined;
  isLoading: boolean;
  repasGlisse: RepasPlanning | null;
  setRepasGlisse: (repas: RepasPlanning | null) => void;
  handleDragStart: (event: DragStartEvent) => void;
  handleDragEnd: (event: DragEndEvent) => void;
  datesSemaine: string[];
  jours: string[];
  trouverRepas: (date: string, type: TypeRepas) => RepasPlanning | undefined;
  onAjouter: (date: string, type: TypeRepas) => void;
  onRetirer: (repas: RepasPlanning) => void;
  onModifierChamp?: (repasId: number, champ: string, valeur: string) => void;
  onRegenerer?: (repas: RepasPlanning) => void;
  nomDinerParDescription: Record<string, string>;
}

export function GrillePlanningHebdo({
  modeAffichage,
  chargementMensuel,
  planningMensuel,
  isLoading,
  repasGlisse,
  setRepasGlisse,
  handleDragStart,
  handleDragEnd,
  datesSemaine,
  jours,
  trouverRepas,
  onAjouter,
  onRetirer,
  onModifierChamp,
  onRegenerer,
  nomDinerParDescription,
}: GrillePlanningHebdoProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  if (modeAffichage === "mois") {
    if (chargementMensuel) {
      return <Skeleton className="h-[520px] w-full" />;
    }
    if (planningMensuel) {
      return (
        <div className="animate-in fade-in slide-in-from-bottom-1 duration-500">
          <CalendrierMensuel mois={planningMensuel.mois} parJour={planningMensuel.par_jour} />
        </div>
      );
    }
    return null;
  }

  if (isLoading) {
    return (
      <div className="grid gap-2">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton
            key={i}
            className={`h-24 w-full animate-in fade-in slide-in-from-bottom-1 duration-500 ${STAGGER_DELAYS[i % STAGGER_DELAYS.length]}`}
          />
        ))}
      </div>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={() => setRepasGlisse(null)}
    >
      <div className="space-y-2" data-planning-grid>
        <div className="rounded-2xl border border-dashed bg-muted/35 px-3 py-2 text-xs text-muted-foreground">
          <span className="font-medium text-foreground/80">Astuce :</span> utilisez la poignée{" "}
          <GripVertical className="inline h-3 w-3" /> pour déplacer un repas par glisser-déposer,
          y compris sur mobile.
        </div>
        {datesSemaine.map((date, idx) => {
          const dateObj = new Date(date);
          const estAujourdhui = date === new Date().toISOString().split("T")[0];

          return (
            <Card
              key={date}
              className={`${estAujourdhui ? "border-primary" : ""} animate-in fade-in slide-in-from-bottom-1 duration-500 ${STAGGER_DELAYS[idx % STAGGER_DELAYS.length]}`}
            >
              <CardHeader className="py-2 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium">
                    {jours[idx]}{" "}
                    <span className="text-muted-foreground font-normal">
                      {dateObj.toLocaleDateString("fr-FR", {
                        day: "numeric",
                        month: "short",
                      })}
                    </span>
                  </CardTitle>
                  {estAujourdhui && (
                    <Badge variant="default" className="text-xs">
                      Aujourd'hui
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="py-2 px-4">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {TYPES_REPAS.map(({ valeur, label, emoji }) => (
                    <CaseRepasPlanning
                      key={valeur}
                      date={date}
                      type={valeur}
                      label={label}
                      emoji={emoji}
                      repas={trouverRepas(date, valeur)}
                      repasGlisse={repasGlisse}
                      onAjouter={onAjouter}
                      onRetirer={onRetirer}
                      onModifierChamp={onModifierChamp}
                      onRegenerer={onRegenerer}
                      nomDinerParDescription={nomDinerParDescription}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
      <DragOverlay>
        {repasGlisse ? (
          <div className="rounded-md border bg-background px-3 py-2 text-sm shadow-xl">
            {repasGlisse.recette_nom || repasGlisse.notes || "Repas"}
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
