// ═══════════════════════════════════════════════════════════
// Page Insights & Analytics — "Ma famille en chiffres" (P6)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { BarChart3, TrendingUp, TrendingDown, Minus, Lightbulb, RefreshCw } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { SectionReveal, ItemAnime } from "@/composants/ui/motion-utils";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirInsightsAnalytics } from "@/bibliotheque/api/ia-avancee";
import type { InsightAnalytics } from "@/types/ia-avancee";

const ICONE_TENDANCE: Record<string, typeof TrendingUp> = {
  hausse: TrendingUp,
  baisse: TrendingDown,
  stable: Minus,
};

const COULEUR_TENDANCE: Record<string, string> = {
  hausse: "text-green-600",
  baisse: "text-red-500",
  stable: "text-muted-foreground",
};

function CarteInsight({ insight }: { insight: InsightAnalytics }) {
  const IconeTendance = ICONE_TENDANCE[insight.tendance] ?? Minus;
  const couleur = COULEUR_TENDANCE[insight.tendance] ?? "text-muted-foreground";

  return (
    <Card>
      <CardContent className="pt-4 pb-4 space-y-1">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            {insight.categorie}
          </p>
          <IconeTendance className={`h-4 w-4 ${couleur}`} />
        </div>
        <p className="text-lg font-bold">{insight.valeur}</p>
        <p className="text-sm font-medium">{insight.titre}</p>
        {insight.detail && (
          <p className="text-xs text-muted-foreground">{insight.detail}</p>
        )}
      </CardContent>
    </Card>
  );
}

export default function PageInsights() {
  const [periode, setPeriode] = useState("3");

  const {
    data: insights,
    isLoading,
    refetch,
    isFetching,
  } = utiliserRequete(
    ["insights-analytics", periode],
    () => obtenirInsightsAnalytics(Number(periode)),
    { staleTime: 5 * 60 * 1000 }
  );

  return (
    <div className="space-y-6">
      <SectionReveal>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-indigo-600" />
              Ma famille en chiffres
            </h1>
            <p className="text-muted-foreground">
              Tendances et insights générés par l&apos;IA sur {periode} mois
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Select value={periode} onValueChange={setPeriode}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1 mois</SelectItem>
                <SelectItem value="3">3 mois</SelectItem>
                <SelectItem value="6">6 mois</SelectItem>
                <SelectItem value="12">12 mois</SelectItem>
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              onClick={() => void refetch()}
              disabled={isFetching}
            >
              <RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
      </SectionReveal>

      {/* Score global */}
      {insights?.score_global != null && (
        <SectionReveal delay={0.02}>
          <Card className="border-indigo-300/60 bg-indigo-50/50 dark:border-indigo-900/50 dark:bg-indigo-950/20">
            <CardContent className="pt-4 pb-4 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/50">
                <span className="text-2xl font-bold text-indigo-700 dark:text-indigo-300">
                  {insights.score_global}
                </span>
              </div>
              <div>
                <p className="font-semibold">Score global famille</p>
                <p className="text-sm text-muted-foreground">
                  Sur la période de {insights.periode_mois} mois analysés
                </p>
              </div>
            </CardContent>
          </Card>
        </SectionReveal>
      )}

      {/* Insights grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="pt-4 pb-4 space-y-2">
                <div className="h-3 w-20 bg-muted rounded" />
                <div className="h-6 w-16 bg-muted rounded" />
                <div className="h-4 w-32 bg-muted rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : insights?.insights?.length ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {insights.insights.map((insight, i) => (
            <ItemAnime key={`${insight.categorie}-${i}`} delay={i * 0.04}>
              <CarteInsight insight={insight} />
            </ItemAnime>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <BarChart3 className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p>Pas encore assez de données pour générer des insights.</p>
            <p className="text-xs mt-1">Utilisez l&apos;app quelques semaines pour voir les tendances.</p>
          </CardContent>
        </Card>
      )}

      {/* Recommandations */}
      {insights?.recommandations?.length ? (
        <SectionReveal delay={0.08}>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-amber-500" />
                Recommandations IA
              </CardTitle>
              <CardDescription>
                Suggestions basées sur les tendances observées
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {insights.recommandations.map((reco, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm"
                  >
                    <Badge variant="outline" className="mt-0.5 shrink-0 text-[10px]">
                      {i + 1}
                    </Badge>
                    {reco}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </SectionReveal>
      ) : null}
    </div>
  );
}
