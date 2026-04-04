"use client";

import Link from "next/link";
import {
  Brain,
  ChefHat,
  Heart,
  RefreshCw,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirPreferencesApprises } from "@/bibliotheque/api/avance";

function formatScore(score: number): string {
  return `${Math.round(score * 100)}%`;
}

export default function PagePreferencesApprises() {
  const {
    data,
    isLoading,
    isFetching,
    refetch,
  } = utiliserRequete(
    ["innovations", "preferences-apprises"],
    obtenirPreferencesApprises,
    { staleTime: 15 * 60 * 1000 }
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Brain className="h-6 w-6 text-violet-600" />
            Préférences IA apprises
          </h1>
          <p className="text-muted-foreground">
            Visualisez ce que l&apos;IA retient réellement des goûts et habitudes de la famille.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => void refetch()} disabled={isFetching}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? "animate-spin" : ""}`} />
          Actualiser
        </Button>
      </div>

      <Card className="border-violet-300/60 bg-violet-50/40 dark:border-violet-900/50 dark:bg-violet-950/10">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-violet-600" />
            Statut d&apos;apprentissage
          </CardTitle>
          <CardDescription>
            Après deux semaines de signaux stables, les suggestions peuvent être réellement pondérées.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {isLoading ? (
            Array.from({ length: 3 }).map((_, index) => <Skeleton key={index} className="h-24 w-full" />)
          ) : (
            <>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Semaines analysées</p>
                <p className="mt-1 text-2xl font-bold">{data?.semaines_analysees ?? 0}</p>
              </div>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Influence active</p>
                <div className="mt-2">
                  <Badge variant={data?.influence_active ? "default" : "secondary"}>
                    {data?.influence_active ? "Oui, pondération activée" : "Collecte en cours"}
                  </Badge>
                </div>
              </div>
              <div className="rounded-lg border bg-background/80 p-3">
                <p className="text-xs uppercase tracking-wide text-muted-foreground">Signaux disponibles</p>
                <p className="mt-1 text-2xl font-bold">
                  {(data?.preferences_favorites?.length ?? 0) + (data?.preferences_a_eviter?.length ?? 0)}
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Heart className="h-4 w-4 text-rose-500" />
              Favoris détectés
            </CardTitle>
            <CardDescription>
              Ingrédients, styles ou catégories à privilégier dans les suggestions futures.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-28 w-full" />
            ) : data?.preferences_favorites?.length ? (
              <div className="flex flex-wrap gap-2">
                {data.preferences_favorites.map((item) => (
                  <Badge key={`${item.categorie}-${item.valeur}`} variant="outline" className="py-1">
                    {item.valeur} · {formatScore(item.score_confiance)}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Pas encore assez de signaux positifs pour dégager un favori stable.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <TriangleAlert className="h-4 w-4 text-amber-500" />
              À éviter / surveiller
            </CardTitle>
            <CardDescription>
              Eléments à espacer lorsque les retours indiquent une moindre appétence.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-28 w-full" />
            ) : data?.preferences_a_eviter?.length ? (
              <div className="flex flex-wrap gap-2">
                {data.preferences_a_eviter.map((item) => (
                  <Badge key={`${item.categorie}-${item.valeur}`} variant="secondary" className="py-1">
                    {item.valeur} · {formatScore(item.score_confiance)}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucun signal négatif stable n&apos;a été détecté pour le moment.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ChefHat className="h-4 w-4 text-emerald-600" />
            Ajustements suggérés par l&apos;IA
          </CardTitle>
          <CardDescription>
            Comment ces apprentissages influencent concrètement le planning et les recommandations.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : data?.ajustements_suggestions?.length ? (
            <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1">
              {data.ajustements_suggestions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">Aucun ajustement spécifique n&apos;est encore disponible.</p>
          )}

          <div className="flex flex-wrap gap-2 pt-2">
            <Button asChild size="sm">
              <Link href="/cuisine/planning">Voir le planning repas</Link>
            </Button>
            <Button asChild variant="outline" size="sm">
              <Link href="/outils/resume-ia">Ouvrir le résumé IA</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
