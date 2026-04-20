'use client'

import { ChevronDown } from "lucide-react";
import { CalendrierMosaiqueRepas } from "@/composants/planning/calendrier-mosaique-repas";
import { CalendrierColonnesPlanning } from "@/composants/planning/calendrier-colonnes-planning";
import type { RepasPlanning } from "@/types/planning";

interface VuesSupplementairesPlanningProps {
  dates: string[];
  repasParJour: Record<string, RepasPlanning[]>;
  ouvert: boolean;
  onToggle: () => void;
}

export function VuesSupplementairesPlanning({
  dates,
  repasParJour,
  ouvert,
  onToggle,
}: VuesSupplementairesPlanningProps) {
  return (
    <div className="animate-in fade-in slide-in-from-bottom-1 duration-500 delay-300">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between rounded-xl border border-dashed bg-muted/30 px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground"
      >
        <span className="font-medium">Vues supplémentaires — mosaïque &amp; colonnes</span>
        <ChevronDown
          className={`h-4 w-4 shrink-0 transition-transform duration-200 ${
            ouvert ? "rotate-180" : ""
          }`}
        />
      </button>
      {ouvert && (
        <div className="mt-3 space-y-4">
          <CalendrierMosaiqueRepas dates={dates} repasParJour={repasParJour} />
          <CalendrierColonnesPlanning dates={dates} repasParJour={repasParJour} />
        </div>
      )}
    </div>
  );
}
