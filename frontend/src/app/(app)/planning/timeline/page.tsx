// ═══════════════════════════════════════════════════════════
// Timeline — Vue chronologique de la semaine
// ═══════════════════════════════════════════════════════════

"use client";

import { CalendarDays, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/composants/ui/button";
import { EtatVidePlanning } from "@/composants/planning/etat-vide-planning";
import { TimelineSemaine } from "@/composants/planning/timeline-semaine";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirPlanningSemaine } from "@/bibliotheque/api/planning";

export default function PageTimeline() {
  const { data: planning, isLoading } = utiliserRequete(
    ["planning", "semaine"],
    () => obtenirPlanningSemaine()
  );

  const repas = planning?.repas ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🕐 Timeline</h1>
          <p className="text-muted-foreground">
            Vue chronologique des repas de la semaine
          </p>
        </div>
        <Link href="/planning">
          <Button variant="outline" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Calendrier
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : repas.length === 0 ? (
        <EtatVidePlanning
          icon={<CalendarDays className="h-8 w-8" />}
          message="Aucun repas planifié cette semaine"
        />
      ) : (
        <TimelineSemaine repas={repas} />
      )}
    </div>
  );
}
