// ═══════════════════════════════════════════════════════════
// Anti-Gaspillage — Score, alertes et recettes rescue
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import {
  Leaf,
  AlertTriangle,
  Clock,
  TrendingDown,
  Euro,
  ChefHat,
  Loader2,
  Trophy,
  BarChart2,
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
import { obtenirAntiGaspillage, obtenirHistoriqueGaspillage } from "@/bibliotheque/api/anti-gaspillage";

function couleurScore(score: number): string {
  if (score >= 80) return "text-green-600 dark:text-green-400";
  if (score >= 50) return "text-orange-500 dark:text-orange-400";
  return "text-red-500 dark:text-red-400";
}

function badgeJours(jours: number) {
  if (jours <= 1)
    return (
      <Badge variant="destructive" className="text-xs">
        Demain
      </Badge>
    );
  if (jours <= 3)
    return (
      <Badge className="text-xs bg-orange-500 hover:bg-orange-600">
        {jours}j
      </Badge>
    );
  return (
    <Badge variant="secondary" className="text-xs">
      {jours}j
    </Badge>
  );
}

export default function PageAntiGaspillage() {
  const { data, isLoading } = utiliserRequete(
    ["anti-gaspillage"],
    () => obtenirAntiGaspillage()
  );

  const { data: historique } = utiliserRequete(
    ["anti-gaspillage", "historique"],
    () => obtenirHistoriqueGaspillage()
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            🌱 Anti-Gaspillage
          </h1>
          <p className="text-muted-foreground">Chargement...</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  const score = data?.score;
  const articlesUrgents = data?.articles_urgents ?? [];
  const recettesRescue = data?.recettes_rescue ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          🌱 Anti-Gaspillage
        </h1>
        <p className="text-muted-foreground">
          Réduisez le gaspillage et économisez
        </p>
      </div>

      {/* Métriques score */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Leaf className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Score</p>
                <p className={`text-3xl font-bold ${couleurScore(score?.score ?? 0)}`}>
                  {score?.score ?? 0}
                  <span className="text-lg">/100</span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <TrendingDown className="h-8 w-8 text-red-500" />
              <div>
                <p className="text-sm text-muted-foreground">Périmés ce mois</p>
                <p className="text-2xl font-bold">
                  {score?.articles_perimes_mois ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Leaf className="h-8 w-8 text-emerald-500" />
              <div>
                <p className="text-sm text-muted-foreground">Sauvés ce mois</p>
                <p className="text-2xl font-bold">
                  {score?.articles_sauves_mois ?? 0}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Euro className="h-8 w-8 text-yellow-500" />
              <div>
                <p className="text-sm text-muted-foreground">Économie estimée</p>
                <p className="text-2xl font-bold">
                  {(score?.economie_estimee ?? 0).toFixed(0)}€
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Articles urgents */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              Articles bientôt périmés
            </CardTitle>
            <CardDescription>
              {articlesUrgents.length} article
              {articlesUrgents.length > 1 ? "s" : ""} à utiliser rapidement
            </CardDescription>
          </CardHeader>
          <CardContent>
            {articlesUrgents.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-6">
                Aucun article urgent — bravo !
              </p>
            ) : (
              <div className="space-y-2">
                {articlesUrgents.map((a) => (
                  <div
                    key={a.id}
                    className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-accent transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">{a.nom}</p>
                      <p className="text-xs text-muted-foreground">
                        {a.quantite ? `${a.quantite}${a.unite ? " " + a.unite : ""}` : ""}
                        {a.quantite ? " · " : ""}
                        Expire le{" "}
                        {new Date(a.date_peremption).toLocaleDateString("fr-FR")}
                      </p>
                    </div>
                    {badgeJours(a.jours_restants)}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recettes rescue */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <ChefHat className="h-5 w-5 text-primary" />
              Recettes rescue
            </CardTitle>
            <CardDescription>
              Utilisez vos ingrédients avant qu&apos;il ne soit trop tard
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recettesRescue.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-6">
                Aucune recette rescue à proposer
              </p>
            ) : (
              <div className="space-y-2">
                {recettesRescue.map((r) => (
                  <Link
                    key={r.id}
                    href={`/cuisine/recettes/${r.id}`}
                    className="flex items-center justify-between rounded-md px-3 py-2 hover:bg-accent transition-colors"
                  >
                    <div>
                      <p className="text-sm font-medium">{r.nom}</p>
                      <div className="flex gap-1 mt-1">
                        {r.ingredients_utilises.map((ing) => (
                          <Badge
                            key={ing}
                            variant="outline"
                            className="text-xs"
                          >
                            {ing}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground shrink-0">
                      {r.temps_total && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {r.temps_total} min
                        </span>
                      )}
                      {r.difficulte && (
                        <Badge variant="secondary" className="text-xs">
                          {r.difficulte}
                        </Badge>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Historique hebdomadaire */}
      {historique && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart2 className="h-5 w-5 text-primary" />
              Historique (4 dernières semaines)
            </CardTitle>
            <CardDescription>
              Score moyen : <strong>{historique.score_moyen_4s}/100</strong>
              {" · "}Tendance :{" "}
              <span
                className={
                  historique.tendance === "baisse"
                    ? "text-green-600"
                    : historique.tendance === "hausse"
                    ? "text-red-500"
                    : "text-muted-foreground"
                }
              >
                {historique.tendance === "baisse"
                  ? "↓ En amélioration"
                  : historique.tendance === "hausse"
                  ? "↑ À surveiller"
                  : "→ Stable"}
              </span>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {historique.semaines.map((s, i) => (
                <div key={i} className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground w-24 shrink-0">
                    {new Date(s.debut).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}
                  </span>
                  <div className="flex-1 h-5 rounded-full bg-muted overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        s.score >= 80
                          ? "bg-green-500"
                          : s.score >= 50
                          ? "bg-orange-400"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${s.score}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium w-10 text-right">{s.score}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Badges */}
      {historique && historique.badges.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              Trophées anti-gaspillage
            </CardTitle>
            <CardDescription>
              {historique.badges.filter((b) => b.obtenu).length} / {historique.badges.length} obtenus
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {historique.badges.map((b) => (
                <div
                  key={b.id}
                  className={`flex items-start gap-3 rounded-lg border p-3 transition-opacity ${
                    b.obtenu ? "" : "opacity-40 grayscale"
                  }`}
                >
                  <span className="text-2xl">{b.emoji}</span>
                  <div>
                    <p className="text-sm font-semibold">{b.nom}</p>
                    <p className="text-xs text-muted-foreground">{b.description}</p>
                    {!b.obtenu && b.condition_valeur && (
                      <p className="text-xs text-primary mt-1">
                        {b.valeur_actuelle ?? 0} / {b.condition_valeur}
                      </p>
                    )}
                  </div>
                  {b.obtenu && (
                    <Badge className="ml-auto shrink-0 text-xs bg-yellow-500 hover:bg-yellow-600">
                      ✓
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
