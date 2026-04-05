"use client";

import { useEffect, useMemo, useState } from "react";
import { GripVertical, RotateCcw } from "lucide-react";
import { Button } from "@/composants/ui/button";

export interface WidgetDraggable {
  id: string;
  titre: string;
}

interface GrilleWidgetsProps<T extends WidgetDraggable> {
  stockageCle: string;
  items: T[];
  classeGrille: string;
  titre?: string;
  renderItem: (item: T, index: number) => React.ReactNode;
}

function reordonner<T>(liste: T[], source: number, destination: number): T[] {
  const copie = [...liste];
  const [deplace] = copie.splice(source, 1);
  copie.splice(destination, 0, deplace);
  return copie;
}

export function GrilleWidgets<T extends WidgetDraggable>({
  stockageCle,
  items,
  classeGrille,
  titre,
  renderItem,
}: GrilleWidgetsProps<T>) {
  const [ordre, setOrdre] = useState<string[]>([]);
  const [dragId, setDragId] = useState<string | null>(null);

  useEffect(() => {
    const brut = localStorage.getItem(stockageCle);
    if (brut) {
      try {
        const ids = JSON.parse(brut) as string[];
        setOrdre(ids);
        return;
      } catch {
        // Ignorer un stockage invalide et retomber sur l'ordre par defaut.
      }
    }
    setOrdre(items.map((i) => i.id));
  }, [items, stockageCle]);

  useEffect(() => {
    if (ordre.length > 0) {
      localStorage.setItem(stockageCle, JSON.stringify(ordre));
    }
  }, [ordre, stockageCle]);

  const ordreEffectif = useMemo(() => {
    const idsConnus = new Set(items.map((i) => i.id));
    const nettoye = ordre.filter((id) => idsConnus.has(id));
    const manquants = items.map((i) => i.id).filter((id) => !nettoye.includes(id));
    return [...nettoye, ...manquants];
  }, [items, ordre]);

  const itemsOrdonnes = useMemo(() => {
    const map = new Map(items.map((i) => [i.id, i]));
    return ordreEffectif.map((id) => map.get(id)).filter(Boolean) as T[];
  }, [items, ordreEffectif]);

  const resetOrdre = () => {
    const initial = items.map((i) => i.id);
    setOrdre(initial);
    localStorage.setItem(stockageCle, JSON.stringify(initial));
  };

  const onDropSur = (cibleId: string) => {
    if (!dragId || dragId === cibleId) return;
    const source = ordreEffectif.indexOf(dragId);
    const destination = ordreEffectif.indexOf(cibleId);
    if (source < 0 || destination < 0) return;
    setOrdre(reordonner(ordreEffectif, source, destination));
    setDragId(null);
  };

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        {titre ? <h2 className="text-lg font-semibold">{titre}</h2> : <div />}
        <Button variant="ghost" size="sm" onClick={resetOrdre} className="gap-1 text-xs">
          <RotateCcw className="h-3.5 w-3.5" />
          Reinitialiser
        </Button>
      </div>
      <div className={classeGrille}>
        {itemsOrdonnes.map((item, index) => (
          <div
            key={item.id}
            draggable
            onDragStart={(e) => {
              setDragId(item.id);
              e.dataTransfer.effectAllowed = "move";
            }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => onDropSur(item.id)}
            className={dragId === item.id ? "opacity-60" : ""}
          >
            <div className="mb-1 flex items-center gap-1 text-[11px] text-muted-foreground">
              <GripVertical className="h-3.5 w-3.5" />
              Glisser pour reordonner
            </div>
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </section>
  );
}
