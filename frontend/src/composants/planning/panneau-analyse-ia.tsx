// ═══════════════════════════════════════════════════════════
// PanneauAnalyseIAPlanning — panneau d'analyse IA de la semaine
// ═══════════════════════════════════════════════════════════

"use client";

import { Sparkles } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import type {
  AnalyseVarieteResponse,
  OptimisationNutritionPlanningResponse,
  SimplificationPlanningResponse,
} from "@/bibliotheque/api/ia-modules";

export type AnalysePlanningIaResultat = {
  variete: AnalyseVarieteResponse;
  nutrition: OptimisationNutritionPlanningResponse;
  simplification: SimplificationPlanningResponse;
};

export function PanneauAnalyseIAPlanning({
  analyse,
  enChargement,
  peutAnalyser,
  onAnalyser,
  onOuvrirModalGeneration,
}: {
  analyse: AnalysePlanningIaResultat | null;
  enChargement: boolean;
  peutAnalyser: boolean;
  onAnalyser: () => void;
  onOuvrirModalGeneration: (platsInitiaux: string[]) => void;
}) {
  return (
    <Card className="border-violet-200/70 bg-violet-50/40 dark:border-violet-900/50 dark:bg-violet-950/10">
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle className="text-base">🧠 Analyse IA de la semaine</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Vérifiez en un clic la variété, l'équilibre nutritionnel et la charge cuisine du
              planning actuel.
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={onAnalyser}
            disabled={enChargement || !peutAnalyser}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            {enChargement ? "Analyse..." : "Analyser la semaine"}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {analyse ? (
          <>
            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Variété</p>
                <p className="mt-1 text-2xl font-bold text-violet-600">
                  {analyse.variete.score_variete}/100
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {(analyse.variete.types_cuisines ?? []).length} styles culinaires détectés
                </p>
              </div>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  Fruits &amp; légumes
                </p>
                <p className="mt-1 text-2xl font-bold text-emerald-600">
                  {Math.round(analyse.nutrition.fruits_legumes_quota * 100)}%
                </p>
                <p className="text-xs text-muted-foreground mt-1">Objectif hebdo estimé</p>
              </div>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">
                  Charge cuisine
                </p>
                <p className="mt-1 text-2xl font-bold text-amber-600">
                  {analyse.simplification.gain_temps_minutes} min
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Gain potentiel ({analyse.simplification.charge_globale})
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge
                variant={analyse.variete.proteins_bien_repartis ? "default" : "secondary"}
              >
                Protéines{" "}
                {analyse.variete.proteins_bien_repartis ? "bien réparties" : "à renforcer"}
              </Badge>
              <Badge variant={analyse.nutrition.equilibre_fibre ? "default" : "secondary"}>
                Fibres {analyse.nutrition.equilibre_fibre ? "OK" : "à surveiller"}
              </Badge>
              <Badge variant="outline">
                {analyse.simplification.nb_recettes_complexes} recette(s) complexes
              </Badge>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-lg border bg-background/80 p-3 space-y-2">
                <p className="text-sm font-semibold">À privilégier</p>
                <p className="text-xs text-muted-foreground">
                  {(analyse.nutrition.aliments_a_privilegier ?? []).join(" · ") || "RAS"}
                </p>
                {(analyse.variete.recommandations ?? []).length > 0 && (
                  <>
                    <p className="text-sm font-semibold pt-1">Idées de variété</p>
                    <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                      {(analyse.variete.recommandations ?? []).slice(0, 3).map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
              <div className="rounded-lg border bg-background/80 p-3 space-y-2">
                <p className="text-sm font-semibold">Charge &amp; simplification</p>
                <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                  {(analyse.simplification.suggestions_simplification ?? []).slice(0, 3).map(
                    (item) => (
                      <li key={item}>{item}</li>
                    )
                  )}
                </ul>
                {(analyse.variete.repetitions_problematiques ?? []).length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Répétitions à surveiller :{" "}
                    {(analyse.variete.repetitions_problematiques ?? []).join(", ")}
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <Button
                size="sm"
                variant="default"
                className="bg-violet-600 hover:bg-violet-700 text-white"
                onClick={() => {
                  const platsSuggeres = [
                    ...(analyse.nutrition.aliments_a_privilegier ?? []),
                    ...(analyse.variete.recommandations ?? []),
                  ].slice(0, 8);
                  onOuvrirModalGeneration(platsSuggeres);
                }}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Régénérer en appliquant ces conseils
              </Button>
            </div>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">
            Lancez l'analyse pour obtenir un score de variété, un bilan nutritionnel et des
            suggestions de simplification.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
