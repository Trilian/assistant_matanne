// ═══════════════════════════════════════════════════════════
// Budget Insights IA — Prédictions, Anomalies, Économies
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Sparkles,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  Lightbulb,
  Brain,
  ChevronDown,
  ChevronUp,
  BadgeEuro,
  ShieldAlert,
  Info,
  Loader2,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirAnalyseBudgetIA } from "@/bibliotheque/api/famille";
import type {
  AnalyseBudgetIA,
  PredictionCategorie,
  AnomalieBudget,
  SuggestionEconomie,
} from "@/bibliotheque/api/famille";

// ── Sous-composants ──

function IconeTendance({ tendance }: { tendance: string }) {
  if (tendance === "hausse") return <TrendingUp className="h-4 w-4 text-destructive" />;
  if (tendance === "baisse") return <TrendingDown className="h-4 w-4 text-green-600" />;
  return <Minus className="h-4 w-4 text-muted-foreground" />;
}

function BadgeSeverite({ severite }: { severite: string }) {
  if (severite === "danger")
    return <Badge variant="destructive">Alerte</Badge>;
  if (severite === "warning")
    return <Badge className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">Attention</Badge>;
  return <Badge variant="outline">Info</Badge>;
}

function IconeSeverite({ severite }: { severite: string }) {
  if (severite === "danger") return <ShieldAlert className="h-5 w-5 text-destructive" />;
  if (severite === "warning") return <AlertTriangle className="h-5 w-5 text-amber-500" />;
  return <Info className="h-5 w-5 text-muted-foreground" />;
}

function BadgeDifficulte({ difficulte }: { difficulte: string }) {
  if (difficulte === "facile")
    return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Facile</Badge>;
  if (difficulte === "difficile")
    return <Badge variant="destructive">Difficile</Badge>;
  return <Badge variant="outline">Moyen</Badge>;
}

// ── Section Prédictions ──

function SectionPredictions({
  predictions,
}: {
  predictions: AnalyseBudgetIA["predictions"];
}) {
  const [ouvert, setOuvert] = useState(true);

  if (!predictions) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-sm text-muted-foreground">
          Pas assez de données pour générer des prédictions. Ajoutez des dépenses sur plusieurs mois.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">Prédiction mois prochain</CardTitle>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setOuvert(!ouvert)}>
            {ouvert ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>
        <CardDescription>{predictions.resume}</CardDescription>
      </CardHeader>
      {ouvert && (
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between rounded-lg bg-primary/5 p-3">
            <span className="text-sm font-medium">Total estimé</span>
            <div className="text-right">
              <p className="text-xl font-bold">{predictions.total_prevu.toFixed(2)} €</p>
              <p className="text-xs text-muted-foreground">
                Confiance: {(predictions.confiance * 100).toFixed(0)}%
              </p>
            </div>
          </div>

          <div className="space-y-2">
            {predictions.par_categorie.map((cat: PredictionCategorie) => (
              <div
                key={cat.categorie}
                className="flex items-center justify-between py-1.5 border-b last:border-0"
              >
                <div className="flex items-center gap-2">
                  <IconeTendance tendance={cat.tendance} />
                  <span className="text-sm capitalize">{cat.categorie}</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium tabular-nums">
                    {cat.montant_prevu.toFixed(2)} €
                  </span>
                  <p className="text-xs text-muted-foreground">{cat.explication}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
}

// ── Section Anomalies ──

function SectionAnomalies({ anomalies }: { anomalies: AnomalieBudget[] }) {
  if (anomalies.length === 0) {
    return (
      <Card>
        <CardContent className="py-6 text-center text-sm text-muted-foreground">
          ✅ Aucune anomalie détectée ce mois-ci. Vos dépenses sont dans la norme !
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-500" />
          <CardTitle className="text-base">Anomalies détectées</CardTitle>
        </div>
        <CardDescription>
          {anomalies.length} anomalie{anomalies.length > 1 ? "s" : ""} identifiée{anomalies.length > 1 ? "s" : ""}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {anomalies.map((a: AnomalieBudget, i: number) => (
          <div
            key={i}
            className="flex items-start gap-3 rounded-lg border p-3"
          >
            <IconeSeverite severite={a.severite} />
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium capitalize">{a.categorie}</span>
                <BadgeSeverite severite={a.severite} />
                <Badge variant="outline" className="text-xs">
                  {a.ecart_pourcent > 0 ? "+" : ""}
                  {a.ecart_pourcent.toFixed(0)}%
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">{a.description}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ── Section Suggestions Économies ──

function SectionSuggestions({
  suggestions,
}: {
  suggestions: SuggestionEconomie[];
}) {
  if (suggestions.length === 0) return null;

  const totalEconomie = suggestions.reduce((sum, s) => sum + s.economie_estimee, 0);

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-500" />
          <CardTitle className="text-base">Suggestions d&apos;économies</CardTitle>
        </div>
        <CardDescription>
          Économie potentielle: jusqu&apos;à {totalEconomie.toFixed(2)} €/mois
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {suggestions.map((s: SuggestionEconomie, i: number) => (
          <div
            key={i}
            className="rounded-lg border p-3 space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BadgeEuro className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">{s.titre}</span>
              </div>
              <div className="flex items-center gap-2">
                <BadgeDifficulte difficulte={s.difficulte} />
                <Badge variant="secondary">
                  ~{s.economie_estimee.toFixed(0)} €/mois
                </Badge>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">{s.description}</p>
            <Badge variant="outline" className="text-xs capitalize">
              {s.categorie}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ── Composant principal ──

export function BudgetInsightsIA() {
  const {
    data: analyse,
    isLoading,
    error,
    refetch,
    isFetching,
  } = utiliserRequete<AnalyseBudgetIA>(
    ["famille", "budget", "analyse-ia"],
    obtenirAnalyseBudgetIA,
    { staleTime: 5 * 60 * 1000 } // 5 min cache
  );

  if (error) {
    return (
      <Card>
        <CardContent className="py-6 text-center">
          <p className="text-sm text-muted-foreground mb-3">
            Impossible de charger l&apos;analyse IA du budget.
          </p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">Insights IA</h2>
          <Sparkles className="h-4 w-4 text-yellow-500" />
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
        >
          {isFetching ? (
            <Loader2 className="h-4 w-4 animate-spin mr-1" />
          ) : (
            <Sparkles className="h-4 w-4 mr-1" />
          )}
          Actualiser
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      ) : analyse ? (
        <>
          <SectionPredictions predictions={analyse.predictions} />
          <SectionAnomalies anomalies={analyse.anomalies} />
          <SectionSuggestions suggestions={analyse.suggestions} />
        </>
      ) : null}
    </div>
  );
}
