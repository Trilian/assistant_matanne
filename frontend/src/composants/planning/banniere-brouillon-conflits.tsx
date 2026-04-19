'use client';

import { Loader2 } from 'lucide-react';
import { Button } from '@/composants/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card';
import { toast } from 'sonner';
import type { RapportConflitsPlanning } from '@/types/planning';
import type { FluxCuisine } from '@/bibliotheque/api/ia-bridges';

interface BanniereBrouillonConflitsProps {
  fluxCuisine: FluxCuisine | undefined | null;
  conflits: RapportConflitsPlanning | undefined | null;
  enValidationPlanning: boolean;
  enRegenerationPlanning: boolean;
  validerBrouillonPlanning: (id: number) => void;
  regenererBrouillonPlanning: (id: number) => void;
}

export function BanniereBrouillonConflits({
  fluxCuisine,
  conflits,
  enValidationPlanning,
  enRegenerationPlanning,
  validerBrouillonPlanning,
  regenererBrouillonPlanning,
}: BanniereBrouillonConflitsProps) {
  return (
    <>
      {fluxCuisine?.etape_actuelle === "valider_planning" && fluxCuisine.planning && (
        <Card className="border-amber-300 bg-amber-50/60">
          <CardContent className="py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-amber-900">Brouillon planning en attente de validation</p>
              <p className="text-xs text-amber-800/90">
                Validez ce brouillon pour débloquer la génération et la confirmation des courses.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                onClick={() => validerBrouillonPlanning(fluxCuisine.planning!.id)}
                disabled={enValidationPlanning || enRegenerationPlanning}
              >
                {enValidationPlanning && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {enValidationPlanning ? "Validation en cours…" : "Valider"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  const cible = document.querySelector("[data-planning-grid]");
                  cible?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
                disabled={enValidationPlanning || enRegenerationPlanning}
              >
                Modifier
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => regenererBrouillonPlanning(fluxCuisine.planning!.id)}
                disabled={enValidationPlanning || enRegenerationPlanning}
              >
                {enRegenerationPlanning ? "Régénération…" : "Régénérer"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {conflits && conflits.items.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">⚠️ Conflits détectés</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">{conflits.resume}</p>
            {conflits.items.slice(0, 5).map((conflit, index) => (
              <div key={`${conflit.date_jour}-${index}`} className="rounded-md border p-3">
                <p className="text-sm font-medium">{conflit.message}</p>
                {conflit.suggestion && (
                  <p className="text-xs text-muted-foreground mt-0.5">Suggestion: {conflit.suggestion}</p>
                )}
                <div className="mt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => toast.info("Aide à la résolution rapide bientôt disponible")}
                  >
                    Résoudre rapidement
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </>
  );
}
