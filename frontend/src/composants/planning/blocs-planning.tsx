"use client";

import { Sparkles, Loader2, CookingPot, CalendarDays } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import type { GenererCoursesResult } from "@/bibliotheque/api/courses";
import type { GenererSessionDepuisPlanningResult } from "@/types/batch-cooking";
import type { AnalysePlanningIaResultat } from "@/composants/planning/panneau-analyse-ia";

type SectionAnalyseIaPlanningProps = {
  analysePlanningIa: AnalysePlanningIaResultat | null;
  enAnalysePlanningIA: boolean;
  nbLignesAnalyse: number;
  onAnalyser: () => void;
  onRegenererAvecConseils: (platsSuggeres: string[]) => void;
};

export function SectionAnalyseIaPlanning({
  analysePlanningIa,
  enAnalysePlanningIA,
  nbLignesAnalyse,
  onAnalyser,
  onRegenererAvecConseils,
}: SectionAnalyseIaPlanningProps) {
  return (
    <Card className="border-violet-200/70 bg-violet-50/40 dark:border-violet-900/50 dark:bg-violet-950/10">
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <CardTitle className="text-base">🧠 Analyse IA de la semaine</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Vérifiez en un clic la variété, l'équilibre nutritionnel et la charge cuisine du planning actuel.
            </p>
          </div>
          <Button
            size="sm"
            variant="outline"
            onClick={onAnalyser}
            disabled={enAnalysePlanningIA || nbLignesAnalyse === 0}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            {enAnalysePlanningIA ? "Analyse..." : "Analyser la semaine"}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {analysePlanningIa ? (
          <>
            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Variété</p>
                <p className="mt-1 text-2xl font-bold text-violet-600">{analysePlanningIa.variete.score_variete}/100</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {(analysePlanningIa.variete.types_cuisines ?? []).length} styles culinaires détectés
                </p>
              </div>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Fruits & légumes</p>
                <p className="mt-1 text-2xl font-bold text-emerald-600">
                  {Math.round(analysePlanningIa.nutrition.fruits_legumes_quota * 100)}%
                </p>
                <p className="text-xs text-muted-foreground mt-1">Objectif hebdo estimé</p>
              </div>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Charge cuisine</p>
                <p className="mt-1 text-2xl font-bold text-amber-600">
                  {analysePlanningIa.simplification.gain_temps_minutes} min
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Gain potentiel ({analysePlanningIa.simplification.charge_globale})
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge variant={analysePlanningIa.variete.proteins_bien_repartis ? "default" : "secondary"}>
                Protéines {analysePlanningIa.variete.proteins_bien_repartis ? "bien réparties" : "à renforcer"}
              </Badge>
              <Badge variant={analysePlanningIa.nutrition.equilibre_fibre ? "default" : "secondary"}>
                Fibres {analysePlanningIa.nutrition.equilibre_fibre ? "OK" : "à surveiller"}
              </Badge>
              <Badge variant="outline">
                {analysePlanningIa.simplification.nb_recettes_complexes} recette(s) complexes
              </Badge>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="rounded-lg border bg-background/80 p-3 space-y-2">
                <p className="text-sm font-semibold">À privilégier</p>
                <p className="text-xs text-muted-foreground">
                  {(analysePlanningIa.nutrition.aliments_a_privilegier ?? []).join(" · ") || "RAS"}
                </p>
                {(analysePlanningIa.variete.recommandations ?? []).length > 0 && (
                  <>
                    <p className="text-sm font-semibold pt-1">Idées de variété</p>
                    <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                      {(analysePlanningIa.variete.recommandations ?? []).slice(0, 3).map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
              <div className="rounded-lg border bg-background/80 p-3 space-y-2">
                <p className="text-sm font-semibold">Charge & simplification</p>
                <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                  {(analysePlanningIa.simplification.suggestions_simplification ?? []).slice(0, 3).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
                {(analysePlanningIa.variete.repetitions_problematiques ?? []).length > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Répétitions à surveiller : {(analysePlanningIa.variete.repetitions_problematiques ?? []).join(", ")}
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
                    ...(analysePlanningIa.nutrition.aliments_a_privilegier ?? []),
                    ...(analysePlanningIa.variete.recommandations ?? []),
                  ].slice(0, 8);
                  onRegenererAvecConseils(platsSuggeres);
                }}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                Régénérer en appliquant ces conseils
              </Button>
            </div>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">
            Lancez l'analyse pour obtenir un score de variété, un bilan nutritionnel et des suggestions de simplification.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

type ContenuDialogueCoursesPlanningProps = {
  coursesResultat: GenererCoursesResult;
  onFermer: () => void;
  onVoirListe: () => void;
};

export function ContenuDialogueCoursesPlanning({
  coursesResultat,
  onFermer,
  onVoirListe,
}: ContenuDialogueCoursesPlanningProps) {
  return (
    <div className="space-y-4">
      <div className="text-sm space-y-1">
        <p className="font-medium">✅ {coursesResultat.total_articles} articles ajoutés</p>
        {coursesResultat.contexte && coursesResultat.contexte.nb_invites > 0 && (
          <p className="text-muted-foreground">👥 Quantités ajustées pour {coursesResultat.contexte.nb_invites} invité(s)</p>
        )}
        {coursesResultat.articles_en_stock > 0 && (
          <p className="text-muted-foreground">📦 {coursesResultat.articles_en_stock} articles déjà en stock (non ajoutés)</p>
        )}
      </div>
      {Object.keys(coursesResultat.par_rayon ?? {}).length > 0 && (
        <div className="space-y-1">
          <p className="text-sm font-medium">Par rayon :</p>
          <div className="grid grid-cols-2 gap-1">
            {Object.entries(coursesResultat.par_rayon ?? {}).map(([rayon, count]) => (
              <div key={rayon} className="flex items-center justify-between text-sm rounded-md bg-muted/50 px-2 py-1">
                <span className="capitalize truncate">{rayon.replace(/_/g, " ")}</span>
                <Badge variant="secondary" className="ml-1 text-xs">{count}</Badge>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="flex justify-end gap-2 pt-2">
        <Button variant="outline" onClick={onFermer}>Fermer</Button>
        <Button onClick={onVoirListe}>Voir la liste</Button>
      </div>
    </div>
  );
}

type ContenuDialogueBatchPlanningProps = {
  batchResultat: GenererSessionDepuisPlanningResult;
  onFermer: () => void;
  onVoirSession: () => void;
};

export function ContenuDialogueBatchPlanning({
  batchResultat,
  onFermer,
  onVoirSession,
}: ContenuDialogueBatchPlanningProps) {
  return (
    <div className="space-y-4">
      <div className="text-sm space-y-1">
        <p className="font-medium">✅ {batchResultat.nom}</p>
        <p className="text-muted-foreground">
          📖 {batchResultat.nb_recettes} recette{batchResultat.nb_recettes > 1 ? "s" : ""} sélectionnée{batchResultat.nb_recettes > 1 ? "s" : ""}
        </p>
        <p className="text-muted-foreground">⏱️ Durée estimée : {batchResultat.duree_estimee} minutes</p>
      </div>
      {(batchResultat.robots_utilises ?? []).length > 0 && (
        <div className="space-y-1">
          <p className="text-sm font-medium">Robots compatibles :</p>
          <div className="flex flex-wrap gap-1">
            {batchResultat.robots_utilises.map((robot) => (
              <Badge key={robot} variant="outline" className="text-xs">
                {robot}
              </Badge>
            ))}
          </div>
        </div>
      )}
      {(batchResultat.recettes ?? []).length > 0 && (
        <div className="space-y-1">
          <p className="text-sm font-medium">Recettes :</p>
          <div className="max-h-40 overflow-y-auto space-y-1">
            {batchResultat.recettes.map((r) => (
              <div key={r.id} className="text-sm rounded-md bg-muted/50 px-2 py-1">
                {r.nom} ({r.portions} portions)
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="flex justify-end gap-2 pt-2">
        <Button variant="outline" onClick={onFermer}>Fermer</Button>
        <Button onClick={onVoirSession}>Voir la session</Button>
      </div>
    </div>
  );
}

type ContenuDialogueModePreparationPlanningProps = {
  enGenerationBatch: boolean;
  onChoisirBatch: () => void;
  onChoisirJourParJour: () => void;
};

export function ContenuDialogueModePreparationPlanning({
  enGenerationBatch,
  onChoisirBatch,
  onChoisirJourParJour,
}: ContenuDialogueModePreparationPlanningProps) {
  return (
    <div className="space-y-3 pt-2">
      <p className="text-sm text-muted-foreground">
        Choisissez comment vous souhaitez préparer les repas de cette semaine.
      </p>

      <button
        className="w-full text-left rounded-lg border p-4 hover:bg-accent transition-colors group"
        onClick={onChoisirBatch}
        disabled={enGenerationBatch}
      >
        <div className="flex items-start gap-3">
          <div className="rounded-md bg-primary/10 p-2 group-hover:bg-primary/20 transition-colors shrink-0">
            <CookingPot className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="font-semibold text-sm">Batch Cooking</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              Préparez tout en une seule session le week-end. Idéal pour gagner du temps en semaine.
            </p>
            {enGenerationBatch && (
              <p className="text-xs text-primary mt-1 flex items-center gap-1">
                <Loader2 className="h-3 w-3 animate-spin" />
                Génération en cours…
              </p>
            )}
          </div>
        </div>
      </button>

      <button
        className="w-full text-left rounded-lg border p-4 hover:bg-accent transition-colors group"
        onClick={onChoisirJourParJour}
      >
        <div className="flex items-start gap-3">
          <div className="rounded-md bg-orange-100 dark:bg-orange-900/30 p-2 group-hover:bg-orange-200 dark:group-hover:bg-orange-900/50 transition-colors shrink-0">
            <CalendarDays className="h-5 w-5 text-orange-600 dark:text-orange-400" />
          </div>
          <div>
            <p className="font-semibold text-sm">Jour par jour</p>
            <p className="text-xs text-muted-foreground mt-0.5">
              Suivez le wizard "Ma Semaine" pour préparer chaque jour avec flexibilité.
            </p>
          </div>
        </div>
      </button>
    </div>
  );
}
