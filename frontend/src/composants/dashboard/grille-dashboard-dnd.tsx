// ═══════════════════════════════════════════════════════════
// Grille Dashboard DnD — Widgets réordonnables par drag-drop
// Utilise @dnd-kit/sortable pour un réordonnancement fluide
// ═══════════════════════════════════════════════════════════

"use client";

import { useCallback } from "react";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { GripVertical } from "lucide-react";
import { cn } from "@/bibliotheque/utils";

interface GrilleDashboardDndProps {
  ordre: string[];
  onOrdreChange: (nouvelOrdre: string[]) => void;
  children: React.ReactNode;
}

function WidgetSortable({
  id,
  children,
}: {
  id: string;
  children: React.ReactNode;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    isDragging,
  } = useSortable({ id });

  return (
    <div ref={setNodeRef} className={cn("group relative", isDragging && "opacity-50") }>
      <button
        type="button"
        className={cn(
          "absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 z-10",
          "opacity-0 group-hover:opacity-100 transition-opacity",
          "cursor-grab active:cursor-grabbing",
          "rounded p-1 bg-muted/80 hover:bg-muted shadow-sm"
        )}
        {...attributes}
        {...listeners}
        aria-label="Réorganiser le widget"
      >
        <GripVertical className="h-4 w-4 text-muted-foreground" />
      </button>
      {children}
    </div>
  );
}

export function GrilleDashboardDnd({
  ordre,
  onOrdreChange,
  children,
}: GrilleDashboardDndProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      if (over && active.id !== over.id) {
        const oldIndex = ordre.indexOf(active.id as string);
        const newIndex = ordre.indexOf(over.id as string);
        const nouvelOrdre = arrayMove(ordre, oldIndex, newIndex);
        onOrdreChange(nouvelOrdre);
      }
    },
    [ordre, onOrdreChange]
  );

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext items={ordre} strategy={verticalListSortingStrategy}>
        {children}
      </SortableContext>
    </DndContext>
  );
}

export { WidgetSortable };
