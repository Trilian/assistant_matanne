// ═══════════════════════════════════════════════════════════
// Résumé Hebdomadaire IA — Phase B
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Brain,
  TrendingUp,
  TrendingDown,
  ShoppingCart,
  Utensils,
  Calendar,
  Star,
  Loader2,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import {
  obtenirResumeHebdo,
  obtenirPrevisionBudget,
  obtenirPredictionsCourses,
  obtenirDigestQuotidien,
  obtenirFluxCuisine,
  obtenirAnomaliesBudget,
  type PrevisionBudget,
  type PredictionCourses,
  type DigestQuotidien,
  type FluxCuisine,
  type AnomalieBudget,
} from "@/bibliotheque/api/ia-bridges";

export default function ResumeHebdoPage() {
  // ── Queries ──
  const resumeQuery = useQuery({
    queryKey: ["resume-hebdo"],
    queryFn: obtenirResumeHebdo,
    staleTime: 1000 * 60 * 30, // 30 min
  });

  const budgetQuery = useQuery({
    queryKey: ["prevision-budget"],
    queryFn: obtenirPrevisionBudget,
    staleTime: 1000 * 60 * 15,
  });

  const predictionsQuery = useQuery({
    queryKey: ["predictions-courses"],
    queryFn: () => obtenirPredictionsCourses(10),
    staleTime: 1000 * 60 * 60,
  });

  const digestQuery = useQuery({
    queryKey: ["digest-quotidien"],
    queryFn: obtenirDigestQuotidien,
    staleTime: 1000 * 60 * 5,
  });

  const fluxQuery = useQuery({
    queryKey: ["flux-cuisine"],
    queryFn: () => obtenirFluxCuisine(),
    staleTime: 1000 * 60 * 5,
  });

  const anomaliesQuery = useQuery({
    queryKey: ["anomalies-budget"],
    queryFn: obtenirAnomaliesBudget,
    staleTime: 1000 * 60 * 15,
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6 text-purple-500" />
            Intelligence IA
          </h1>
          <p className="text-muted-foreground">
            Résumé, prédictions et suggestions personnalisées
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            resumeQuery.refetch();
            budgetQuery.refetch();
            predictionsQuery.refetch();
          }}
          disabled={resumeQuery.isFetching}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${resumeQuery.isFetching ? "animate-spin" : ""}`}
          />
          Actualiser
        </Button>
      </div>

      {/* Digest du jour */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Calendar className="h-5 w-5 text-blue-500" />
            Aujourd&apos;hui
          </CardTitle>
        </CardHeader>
        <CardContent>
          {digestQuery.isLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Chargement...
            </div>
          ) : digestQuery.data ? (
            <div className="grid gap-4 md:grid-cols-3">
              {/* Repas */}
              <div>
                <h4 className="font-medium flex items-center gap-1 mb-2">
                  <Utensils className="h-4 w-4" /> Repas
                </h4>
                {digestQuery.data.repas.length > 0 ? (
                  <ul className="space-y-1 text-sm">
                    {digestQuery.data.repas.map((r, i) => (
                      <li key={i} className="text-muted-foreground">
                        <span className="capitalize">{r.type}</span>: {r.recette}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Aucun repas planifié</p>
                )}
              </div>

              {/* Routines */}
              <div>
                <h4 className="font-medium flex items-center gap-1 mb-2">
                  <CheckCircle2 className="h-4 w-4" /> Routines
                </h4>
                {digestQuery.data.routines.length > 0 ? (
                  <ul className="space-y-1 text-sm">
                    {digestQuery.data.routines.map((r, i) => (
                      <li key={i} className="text-muted-foreground">
                        {r.routine}: {r.taches_restantes} tâche(s)
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Tout est à jour ✓</p>
                )}
              </div>

              {/* Entretien */}
              <div>
                <h4 className="font-medium flex items-center gap-1 mb-2">
                  <AlertTriangle className="h-4 w-4" /> Entretien
                </h4>
                {digestQuery.data.entretien.length > 0 ? (
                  <ul className="space-y-1 text-sm">
                    {digestQuery.data.entretien.map((t, i) => (
                      <li key={i} className="text-muted-foreground">
                        {t.nom}
                        <Badge variant={t.priorite === "haute" ? "destructive" : "secondary"} className="ml-2 text-xs">
                          {t.priorite}
                        </Badge>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Aucune tâche urgente</p>
                )}
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Flux cuisine */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Utensils className="h-5 w-5 text-orange-500" />
              Flux Cuisine
            </CardTitle>
          </CardHeader>
          <CardContent>
            {fluxQuery.isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : fluxQuery.data ? (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    {fluxQuery.data.etape_actuelle === "termine"
                      ? "✓ Semaine prête"
                      : fluxQuery.data.etape_actuelle.replace(/_/g, " ")}
                  </Badge>
                  {fluxQuery.data.courses && (
                    <span className="text-sm text-muted-foreground">
                      {fluxQuery.data.courses.progression}%
                    </span>
                  )}
                </div>
                {fluxQuery.data.actions_suivantes.map((action, i) => (
                  <Link key={i} href={action.url || "#"}>
                    <Button variant="ghost" size="sm" className="w-full justify-between">
                      {action.label}
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </Link>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>

        {/* Budget prévision */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="h-5 w-5 text-green-500" />
              Prévision Budget
            </CardTitle>
          </CardHeader>
          <CardContent>
            {budgetQuery.isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : budgetQuery.data ? (
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Dépenses actuelles</span>
                  <span className="font-semibold">{budgetQuery.data.depenses_actuelles}€</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Prévision fin de mois</span>
                  <span className="font-semibold">{budgetQuery.data.prevision_fin_mois}€</span>
                </div>
                {budgetQuery.data.ecart_prevu_pct !== null && (
                  <div className="flex items-center gap-1 text-sm">
                    {budgetQuery.data.ecart_prevu_pct > 0 ? (
                      <TrendingUp className="h-4 w-4 text-red-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-green-500" />
                    )}
                    <span>{Math.abs(budgetQuery.data.ecart_prevu_pct)}% vs budget ref</span>
                  </div>
                )}
              </div>
            ) : null}

            {/* Anomalies */}
            {anomaliesQuery.data && anomaliesQuery.data.length > 0 && (
              <div className="mt-4 pt-3 border-t">
                <h4 className="text-sm font-medium text-red-600 mb-2">
                  ⚠️ Anomalies détectées
                </h4>
                {anomaliesQuery.data.slice(0, 3).map((a, i) => (
                  <div key={i} className="flex justify-between text-sm py-1">
                    <span>{a.categorie}</span>
                    <Badge variant={a.niveau === "critique" ? "destructive" : "secondary"}>
                      {a.pourcentage}%
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Prédictions courses */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <ShoppingCart className="h-5 w-5 text-green-500" />
            Prédictions Courses
          </CardTitle>
        </CardHeader>
        <CardContent>
          {predictionsQuery.isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : predictionsQuery.data && predictionsQuery.data.length > 0 ? (
            <div className="grid gap-2 md:grid-cols-2">
              {predictionsQuery.data.map((p, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2 rounded-md border"
                >
                  <div>
                    <span className="font-medium">{p.nom}</span>
                    <span className="text-xs text-muted-foreground ml-2">
                      {p.categorie}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">
                      {Math.round(p.score_confiance * 100)}%
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      tous les {p.frequence_jours}j
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Pas assez d&apos;historique pour des prédictions
            </p>
          )}
        </CardContent>
      </Card>

      {/* Résumé IA */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Star className="h-5 w-5 text-yellow-500" />
            Résumé de la Semaine
          </CardTitle>
        </CardHeader>
        <CardContent>
          {resumeQuery.isLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Génération du résumé IA...
            </div>
          ) : resumeQuery.data ? (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <p className="whitespace-pre-wrap">{resumeQuery.data.resume}</p>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Le résumé sera disponible dimanche soir
            </p>
          )}
        </CardContent>
      </Card>

      {/* Liens rapides */}
      <div className="grid gap-3 md:grid-cols-4">
        <Link href="/outils/chat-ia">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <Brain className="h-5 w-5 text-purple-500" />
              <span className="text-sm font-medium">Chat IA</span>
            </CardContent>
          </Card>
        </Link>
        <Link href="/famille/budget">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <span className="text-sm font-medium">Budget détaillé</span>
            </CardContent>
          </Card>
        </Link>
        <Link href="/cuisine/courses">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <ShoppingCart className="h-5 w-5 text-blue-500" />
              <span className="text-sm font-medium">Courses</span>
            </CardContent>
          </Card>
        </Link>
        <Link href="/cuisine/ma-semaine">
          <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
            <CardContent className="p-4 flex items-center gap-3">
              <Calendar className="h-5 w-5 text-orange-500" />
              <span className="text-sm font-medium">Ma semaine</span>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
