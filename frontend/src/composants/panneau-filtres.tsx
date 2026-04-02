// ═══════════════════════════════════════════════════════════
// PanneauFiltres — Panneau latéral de filtres réutilisable
// Sprint 20.7 — Filtres avancés sidebar
// ═══════════════════════════════════════════════════════════

"use client";

import { type ReactNode } from "react";
import { SlidersHorizontal, X } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/composants/ui/sheet";
import { Separator } from "@/composants/ui/separator";

interface PanneauFiltresProps {
  /** Nombre de filtres actifs (affiche le badge) */
  nombreFiltresActifs: number;
  /** Callback pour réinitialiser tous les filtres */
  onReinitialiser: () => void;
  /** Contenu du panneau (sections de filtres) */
  children: ReactNode;
  /** Label du bouton déclencheur */
  labelBouton?: string;
}

export function PanneauFiltres({
  nombreFiltresActifs,
  onReinitialiser,
  children,
  labelBouton = "Filtres",
}: PanneauFiltresProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2 relative">
          <SlidersHorizontal className="h-4 w-4" />
          {labelBouton}
          {nombreFiltresActifs > 0 && (
            <Badge className="ml-1 h-4 w-4 p-0 text-[10px] flex items-center justify-center rounded-full">
              {nombreFiltresActifs}
            </Badge>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-72 sm:w-80">
        <SheetHeader className="flex flex-row items-center justify-between pb-2">
          <SheetTitle className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4" />
            {labelBouton}
          </SheetTitle>
          {nombreFiltresActifs > 0 && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1 text-xs text-muted-foreground"
              onClick={onReinitialiser}
            >
              <X className="h-3 w-3" />
              Réinitialiser
            </Button>
          )}
        </SheetHeader>
        <Separator className="mb-4" />
        <div className="space-y-5 overflow-y-auto pb-6">
          {children}
        </div>
      </SheetContent>
    </Sheet>
  );
}

// ─── Section de filtre ────────────────────────────────────────

interface SectionFiltreProps {
  titre: string;
  children: ReactNode;
}

export function SectionFiltre({ titre, children }: SectionFiltreProps) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {titre}
      </p>
      {children}
    </div>
  );
}

// ─── Groupe de boutons toggle ─────────────────────────────────

interface BoutonFiltreProps {
  actif: boolean;
  onClick: () => void;
  children: ReactNode;
  className?: string;
}

export function BoutonFiltre({ actif, onClick, children, className }: BoutonFiltreProps) {
  return (
    <Button
      variant={actif ? "default" : "outline"}
      size="sm"
      onClick={onClick}
      className={`text-xs h-7 ${className ?? ""}`}
    >
      {children}
    </Button>
  );
}
