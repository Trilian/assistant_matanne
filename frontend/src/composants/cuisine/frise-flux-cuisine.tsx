"use client";

import type { LucideIcon } from "lucide-react";
import { ArrowRight, CheckCircle2 } from "lucide-react";

import { cn } from "@/bibliotheque/utils";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Progress } from "@/composants/ui/progress";

export interface EtapeFriseFluxCuisine {
  id: string;
  titre: string;
  description: string;
  icone: LucideIcon;
  resume?: string;
  meta?: string;
  alerte?: boolean;
}

export function FriseFluxCuisine({
  etapes,
  etapeActive = 0,
  progression,
  titre = "Flux interactif repas → inventaire → courses",
  description = "Suivez la semaine en un coup d'œil, du planning à la préparation finale.",
  onSelectionEtape,
}: {
  etapes: EtapeFriseFluxCuisine[];
  etapeActive?: number;
  progression?: number;
  titre?: string;
  description?: string;
  onSelectionEtape?: (index: number) => void;
}) {
  const progressionNormalisee = Math.max(
    0,
    Math.min(
      100,
      progression ?? ((etapeActive + 1) / Math.max(etapes.length, 1)) * 100
    )
  );

  return (
    <Card className="border-primary/10 bg-gradient-to-br from-primary/5 via-background to-emerald-500/5">
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <CardTitle>{titre}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Badge variant="secondary">{Math.round(progressionNormalisee)}% du parcours</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <Progress value={progressionNormalisee} className="h-2" />

        <div className="grid gap-3 xl:grid-cols-4">
          {etapes.map((etape, index) => {
            const statut = index < etapeActive ? "termine" : index === etapeActive ? "actif" : "a_venir";
            const estActif = statut === "actif";
            const estTermine = statut === "termine";
            const Icone = etape.icone;

            return (
              <div key={etape.id} className="relative">
                {index < etapes.length - 1 && (
                  <ArrowRight className="absolute -right-2 top-1/2 hidden h-4 w-4 -translate-y-1/2 text-muted-foreground xl:block" />
                )}

                <button
                  type="button"
                  aria-current={estActif ? "step" : undefined}
                  onClick={() => onSelectionEtape?.(index)}
                  className={cn(
                    "w-full rounded-xl border p-4 text-left transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm",
                    estActif && "border-primary bg-primary/5 shadow-sm ring-1 ring-primary/20",
                    estTermine && "border-emerald-200 bg-emerald-50/60 dark:border-emerald-900 dark:bg-emerald-950/20",
                    !estActif && !estTermine && "border-dashed bg-background/80"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={cn(
                        "mt-0.5 rounded-full p-2",
                        estActif && "bg-primary text-primary-foreground",
                        estTermine && "bg-emerald-600 text-white",
                        !estActif && !estTermine && "bg-muted text-muted-foreground"
                      )}
                    >
                      {estTermine ? <CheckCircle2 className="h-4 w-4" /> : <Icone className="h-4 w-4" />}
                    </div>

                    <div className="min-w-0 flex-1 space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-semibold">{etape.titre}</p>
                        <Badge variant={estActif ? "default" : estTermine ? "secondary" : "outline"}>
                          {estActif ? "En cours" : estTermine ? "Terminé" : "À venir"}
                        </Badge>
                      </div>

                      <p className="text-xs text-muted-foreground">{etape.description}</p>

                      {etape.resume && <p className="pt-1 text-sm font-medium">{etape.resume}</p>}

                      {etape.meta && (
                        <p
                          className={cn(
                            "text-[11px]",
                            etape.alerte ? "text-amber-700 dark:text-amber-300" : "text-muted-foreground"
                          )}
                        >
                          {etape.meta}
                        </p>
                      )}
                    </div>
                  </div>
                </button>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
