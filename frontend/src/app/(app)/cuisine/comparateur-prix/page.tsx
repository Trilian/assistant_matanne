// ═══════════════════════════════════════════════════════════
// Comparateur Prix — Top 20 ingrédients + veille automatique
// Sprint 23 — IN15
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { ShoppingBasket, TrendingDown, TrendingUp, Minus, AlertCircle, RefreshCw, Info } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirComparateurPrixAuto } from "@/bibliotheque/api/avance";
import type { PrixIngredientCompare } from "@/bibliotheque/api/avance";

function iconeVariation(variation: number | null, alerte_soldes: boolean) {
  if (alerte_soldes || (variation !== null && variation <= -10))
    return <TrendingDown className="h-4 w-4 text-green-600" />;
  if (variation !== null && variation > 5)
    return <TrendingUp className="h-4 w-4 text-destructive" />;
  return <Minus className="h-4 w-4 text-muted-foreground" />;
}

function LigneIngredient({ item }: { item: PrixIngredientCompare }) {
  const v = item.variation_pct;
  const labelVariation =
    v === null ? "–" : `${v > 0 ? "+" : ""}${v.toFixed(1)} %`;

  return (
    <div className="flex items-center gap-3 py-3 border-b last:border-0">
      <div className="flex-1 min-w-0">
        <p className="font-medium truncate capitalize">{item.ingredient}</p>
        <p className="text-xs text-muted-foreground">
          Utilisé {item.frequence_utilisation}× •{" "}
          {item.source_prix === "openfoodfacts" ? "OpenFoodFacts" : "historique interne"}
        </p>
      </div>

      {/* Prix historique */}
      <div className="text-right shrink-0 w-20">
        <p className="text-xs text-muted-foreground">Historique</p>
        <p className="text-sm font-medium">
          {item.prix_historique_moyen_eur !== null
            ? `${item.prix_historique_moyen_eur.toFixed(2)} €`
            : "–"}
        </p>
      </div>

      {/* Prix marché */}
      <div className="text-right shrink-0 w-20">
        <p className="text-xs text-muted-foreground">Marché</p>
        <p className="text-sm font-medium">
          {item.prix_marche_eur !== null
            ? `${item.prix_marche_eur.toFixed(2)} €`
            : "–"}
        </p>
      </div>

      {/* Variation */}
      <div className="flex flex-col items-end gap-1 shrink-0 w-24">
        <div className="flex items-center gap-1">
          {iconeVariation(v, item.alerte_soldes)}
          <span
            className={`text-sm font-semibold ${
              v !== null && v <= -10
                ? "text-green-600"
                : v !== null && v > 10
                ? "text-destructive"
                : "text-muted-foreground"
            }`}
          >
            {labelVariation}
          </span>
        </div>
        {item.alerte_soldes && (
          <Badge variant="default" className="text-xs bg-green-600 hover:bg-green-700">
            Soldes
          </Badge>
        )}
      </div>
    </div>
  );
}

export default function ComparateurPrixPage() {
  const [topN, setTopN] = useState(20);

  const { data, isLoading, isFetching, refetch } = utiliserRequete(
    ["innovations", "comparateur-prix", String(topN)],
    () => obtenirComparateurPrixAuto(topN),
    { staleTime: 6 * 60 * 60 * 1000 } // 6h — synchro avec le cache backend
  );

  const nbAlertes = data?.nb_alertes ?? 0;

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <ShoppingBasket className="h-8 w-8" /> Comparateur Prix
          </h1>
          <p className="text-muted-foreground mt-1">
            Veille automatique sur vos ingrédients les plus utilisés
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Sélecteur Top N */}
          <div className="flex gap-1">
            {([10, 20] as const).map((n) => (
              <button
                key={n}
                onClick={() => setTopN(n)}
                className={`px-3 py-1 rounded-md text-sm font-medium border transition-colors ${
                  topN === n
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-border hover:bg-accent"
                }`}
              >
                Top {n}
              </button>
            ))}
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCw className={`h-4 w-4 mr-1 ${isFetching ? "animate-spin" : ""}`} />
            Actualiser
          </Button>
        </div>
      </div>

      {/* Alertes soldes */}
      {!isLoading && nbAlertes > 0 && (
        <Card className="border-green-500/50 bg-green-50/50 dark:bg-green-950/20">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-green-700 dark:text-green-400 flex items-center gap-2">
              <TrendingDown className="h-4 w-4" />
              {nbAlertes} alerte{nbAlertes > 1 ? "s" : ""} soldes détectée{nbAlertes > 1 ? "s" : ""}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {data?.alertes.map((a, i) => (
                <li key={i} className="text-sm text-green-700 dark:text-green-400 flex items-start gap-2">
                  <span className="mt-0.5">•</span>
                  <span>{a}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Tableau ingrédients */}
      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-2">
          <div>
            <CardTitle>
              Top {topN} ingrédients
              {data && (
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  — {data.date_reference}
                </span>
              )}
            </CardTitle>
            <CardDescription className="flex items-center gap-1 mt-1">
              <Info className="h-3 w-3" />
              Prix marché via OpenFoodFacts (meilleure approximation disponible)
            </CardDescription>
          </div>
          {!isLoading && data && (
            <Badge variant="outline">{data.nb_ingredients_analyses} analysés</Badge>
          )}
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full" />
              ))}
            </div>
          ) : !data || data.ingredients.length === 0 ? (
            <div className="flex flex-col items-center py-12 text-muted-foreground gap-3">
              <AlertCircle className="h-8 w-8" />
              <p>Aucun ingrédient à analyser pour l&apos;instant.</p>
              <p className="text-xs">
                Ajoutez des recettes à votre planning pour alimenter le comparateur.
              </p>
            </div>
          ) : (
            <div>
              {data.ingredients.map((item, i) => (
                <LigneIngredient key={i} item={item} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Légende */}
      <Card className="bg-muted/30">
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <TrendingDown className="h-3 w-3 text-green-600" />
              <span>Variation ≤ −10 % → alerte soldes</span>
            </div>
            <div className="flex items-center gap-1">
              <TrendingUp className="h-3 w-3 text-destructive" />
              <span>Variation &gt; +10 % → prix en hausse</span>
            </div>
            <div className="flex items-center gap-1">
              <Minus className="h-3 w-3" />
              <span>Stable ou donnée manquante</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
