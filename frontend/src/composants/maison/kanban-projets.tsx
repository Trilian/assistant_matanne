"use client";

import {
  DndContext,
  PointerSensor,
  closestCorners,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { BotMessageSquare, GripVertical, Trash2 } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import type { ProjetMaison } from "@/types/maison";

const COLONNES = [
  { id: "a_faire", titre: "A faire", style: "border-amber-300/60 bg-amber-50/40 dark:border-amber-900/40 dark:bg-amber-950/20" },
  { id: "en_cours", titre: "En cours", style: "border-blue-300/60 bg-blue-50/40 dark:border-blue-900/40 dark:bg-blue-950/20" },
  { id: "termine", titre: "Termine", style: "border-emerald-300/60 bg-emerald-50/40 dark:border-emerald-900/40 dark:bg-emerald-950/20" },
] as const;

type StatutKanban = (typeof COLONNES)[number]["id"];

function normaliserStatut(statut: string): StatutKanban {
  const valeur = statut
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "_");

  if (valeur.includes("en_cours")) return "en_cours";
  if (valeur.includes("termine")) return "termine";
  return "a_faire";
}

function CarteProjetSortable({
  projet,
  onSupprimer,
  onEstimer,
  enCours,
}: {
  projet: ProjetMaison;
  onSupprimer: (id: number) => void;
  onEstimer: (id: number) => void;
  enCours: boolean;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `projet:${projet.id}`,
  });

  return (
    <Card
      ref={setNodeRef}
      className={isDragging ? "opacity-60" : ""}
      data-dnd-transform={transform ? "active" : "none"}
      data-dnd-transition={transition ? "active" : "none"}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-sm">{projet.nom}</CardTitle>
          <div className="flex items-center gap-1">
            <button
              type="button"
              className="rounded p-1 text-muted-foreground hover:bg-accent"
              aria-label="Deplacer le projet"
              {...attributes}
              {...listeners}
            >
              <GripVertical className="h-3.5 w-3.5" />
            </button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground hover:text-destructive"
              onClick={() => onSupprimer(projet.id)}
              disabled={enCours}
              aria-label={`Supprimer le projet ${projet.nom}`}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardHeader>
      {projet.description && (
        <CardContent className="pt-0 pb-2">
          <p className="line-clamp-2 text-xs text-muted-foreground">{projet.description}</p>
        </CardContent>
      )}
      <CardContent className="pt-0 pb-3">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {projet.priorite && (
            <Badge variant="outline" className="text-xs">
              {projet.priorite}
            </Badge>
          )}
          <Badge variant="secondary" className="text-xs">
            {projet.statut.replace("_", " ")}
          </Badge>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="h-7 w-full gap-1 text-xs"
          onClick={() => onEstimer(projet.id)}
          disabled={enCours}
        >
          <BotMessageSquare className="h-3.5 w-3.5" />
          Estimer IA
        </Button>
      </CardContent>
    </Card>
  );
}

export function KanbanProjets({
  projets,
  onSupprimer,
  onEstimer,
  onDeplacerStatut,
  enCours,
}: {
  projets: ProjetMaison[];
  onSupprimer: (id: number) => void;
  onEstimer: (id: number) => void;
  onDeplacerStatut: (projetId: number, statut: StatutKanban) => void;
  enCours: boolean;
}) {
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));

  const projetsParStatut: Record<StatutKanban, ProjetMaison[]> = {
    a_faire: [],
    en_cours: [],
    termine: [],
  };

  projets.forEach((projet) => {
    projetsParStatut[normaliserStatut(projet.statut)].push(projet);
  });

  const handleDragEnd = (event: DragEndEvent) => {
    if (!event.over) return;

    const active = String(event.active.id);
    const over = String(event.over.id);

    if (!active.startsWith("projet:")) return;
    const projetId = Number(active.replace("projet:", ""));
    if (!Number.isFinite(projetId)) return;

    let statutCible: StatutKanban | null = null;
    if (over.startsWith("colonne:")) {
      statutCible = over.replace("colonne:", "") as StatutKanban;
    } else if (over.startsWith("projet:")) {
      const projetSurvole = projets.find((p) => p.id === Number(over.replace("projet:", "")));
      statutCible = projetSurvole ? normaliserStatut(projetSurvole.statut) : null;
    }

    if (!statutCible) return;
    onDeplacerStatut(projetId, statutCible);
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCorners} onDragEnd={handleDragEnd}>
      <div className="grid gap-3 md:grid-cols-3">
        {COLONNES.map((colonne) => {
          const items = projetsParStatut[colonne.id];
          return (
            <ColonneKanban
              key={colonne.id}
              id={colonne.id}
              titre={colonne.titre}
              style={colonne.style}
              items={items}
              onSupprimer={onSupprimer}
              onEstimer={onEstimer}
              enCours={enCours}
            />
          );
        })}
      </div>
    </DndContext>
  );
}

function ColonneKanban({
  id,
  titre,
  style,
  items,
  onSupprimer,
  onEstimer,
  enCours,
}: {
  id: StatutKanban;
  titre: string;
  style: string;
  items: ProjetMaison[];
  onSupprimer: (id: number) => void;
  onEstimer: (id: number) => void;
  enCours: boolean;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: `colonne:${id}` });

  return (
    <div ref={setNodeRef} className={`rounded-xl border p-2 ${style} ${isOver ? "ring-2 ring-primary/40" : ""}`}>
      <div className="mb-2 flex items-center justify-between px-1">
        <p className="text-sm font-semibold">{titre}</p>
        <Badge variant="secondary" className="text-xs">
          {items.length}
        </Badge>
      </div>

      <SortableContext items={items.map((p) => `projet:${p.id}`)} strategy={verticalListSortingStrategy}>
        <div className="space-y-2">
          {items.map((projet) => (
            <CarteProjetSortable
              key={projet.id}
              projet={projet}
              onSupprimer={onSupprimer}
              onEstimer={onEstimer}
              enCours={enCours}
            />
          ))}
          {items.length === 0 && (
            <div className="rounded-md border border-dashed px-3 py-6 text-center text-xs text-muted-foreground">
              Glisser un projet ici
            </div>
          )}
        </div>
      </SortableContext>
    </div>
  );
}
