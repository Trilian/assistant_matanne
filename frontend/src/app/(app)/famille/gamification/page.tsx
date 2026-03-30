"use client";

import { Award, BarChart3, HeartPulse, Recycle, Trophy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Progress } from "@/composants/ui/progress";
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirPointsFamille,
  obtenirScoreBienEtre,
  obtenirBadgesUtilisateur,
  obtenirHistoriquePoints,
} from "@/bibliotheque/api/tableau-bord";
import type { BadgeDefinition, HistoriquePoints } from "@/bibliotheque/api/tableau-bord";

function BadgeCard({ badge }: { badge: BadgeDefinition }) {
  return (
    <div
      className={`rounded-lg border p-3 transition-colors ${
        badge.obtenu
          ? "border-amber-300 bg-amber-50/50 dark:border-amber-700 dark:bg-amber-950/30"
          : "border-muted bg-muted/30 opacity-60"
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{badge.emoji}</span>
        <div className="min-w-0 flex-1">
          <p className="font-medium">{badge.badge_label}</p>
          <p className="text-xs text-muted-foreground">{badge.description}</p>
          <div className="mt-1 flex items-center gap-2 text-xs">
            <span
              className={`rounded-full px-2 py-0.5 ${
                badge.categorie === "sport"
                  ? "bg-sky-100 text-sky-700 dark:bg-sky-900 dark:text-sky-300"
                  : "bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300"
              }`}
            >
              {badge.categorie}
            </span>
            {badge.obtenu && (
              <span className="text-amber-600 dark:text-amber-400">
                ✓ ×{badge.nb_obtenu ?? 1}
                {badge.derniere_date && ` — ${badge.derniere_date}`}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function HistoriqueChart({ data }: { data: HistoriquePoints[] }) {
  if (!data.length) {
    return <p className="text-sm text-muted-foreground">Aucun historique disponible.</p>;
  }

  const maxTotal = Math.max(...data.map((d) => d.total_points), 1);

  return (
    <div className="space-y-3">
      {data.map((semaine) => (
        <div key={semaine.semaine_debut} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">{semaine.semaine_debut}</span>
            <span className="font-medium">{semaine.total_points} pts</span>
          </div>
          <div className="flex h-4 gap-0.5 overflow-hidden rounded-md">
            <div
              className="bg-sky-400 transition-all"
              style={{ width: `${(semaine.points_sport / maxTotal) * 100}%` }}
              title={`Sport: ${semaine.points_sport}`}
            />
            <div
              className="bg-emerald-400 transition-all"
              style={{ width: `${(semaine.points_alimentation / maxTotal) * 100}%` }}
              title={`Alimentation: ${semaine.points_alimentation}`}
            />
            <div
              className="bg-lime-400 transition-all"
              style={{ width: `${(semaine.points_anti_gaspi / maxTotal) * 100}%` }}
              title={`Anti-gaspi: ${semaine.points_anti_gaspi}`}
            />
          </div>
        </div>
      ))}
      <div className="flex flex-wrap gap-4 pt-1 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-sky-400" /> Sport
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-emerald-400" /> Alimentation
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-sm bg-lime-400" /> Anti-gaspi
        </span>
      </div>
    </div>
  );
}

export default function PageGamificationFamille() {
  const { data: points } = utiliserRequete(["dashboard", "points-famille"], obtenirPointsFamille);
  const { data: score } = utiliserRequete(["dashboard", "score-bienetre"], obtenirScoreBienEtre);
  const { data: badgesData } = utiliserRequete(
    ["dashboard", "badges-utilisateur"],
    obtenirBadgesUtilisateur
  );
  const { data: historiqueData } = utiliserRequete(
    ["dashboard", "historique-points"],
    () => obtenirHistoriquePoints(8)
  );

  const badgesSport = badgesData?.items.filter((b) => b.categorie === "sport") ?? [];
  const badgesNutrition = badgesData?.items.filter((b) => b.categorie === "nutrition") ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Points famille</h1>
        <p className="text-muted-foreground">
          Gamification sport, alimentation et anti-gaspillage pour suivre la dynamique hebdomadaire.
        </p>
      </div>

      {/* ─── Métriques principales ─────────────────────────── */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Total points</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{points?.total_points ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Score bien-être</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <HeartPulse className="h-5 w-5 text-rose-500" />
            <p className="text-3xl font-bold">{score?.score_global ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Pas Garmin</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{points?.details.total_pas ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Badges débloqués</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <Award className="h-5 w-5 text-amber-500" />
            <p className="text-3xl font-bold">
              {badgesData?.obtenus ?? points?.badges.length ?? 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* ─── Barres de progression ─────────────────────────── */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Trophy className="h-4 w-4 text-sky-500" />
              Sport
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-2xl font-semibold">{points?.sport ?? 0}</p>
            <Progress value={Math.round(((points?.sport ?? 0) / 300) * 100)} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <HeartPulse className="h-4 w-4 text-emerald-500" />
              Alimentation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-2xl font-semibold">{points?.alimentation ?? 0}</p>
            <Progress value={Math.round(((points?.alimentation ?? 0) / 300) * 100)} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Recycle className="h-4 w-4 text-lime-500" />
              Anti-gaspi
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-2xl font-semibold">{points?.anti_gaspi ?? 0}</p>
            <Progress value={Math.round(((points?.anti_gaspi ?? 0) / 300) * 100)} />
          </CardContent>
        </Card>
      </div>

      {/* ─── Badges Sport ──────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-sky-500" />
            Badges Sport
          </CardTitle>
        </CardHeader>
        <CardContent>
          {badgesSport.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {badgesSport.map((badge) => (
                <BadgeCard key={badge.badge_type} badge={badge} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Chargement des badges sport…</p>
          )}
        </CardContent>
      </Card>

      {/* ─── Badges Nutrition ──────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HeartPulse className="h-5 w-5 text-emerald-500" />
            Badges Nutrition
          </CardTitle>
        </CardHeader>
        <CardContent>
          {badgesNutrition.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {badgesNutrition.map((badge) => (
                <BadgeCard key={badge.badge_type} badge={badge} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Chargement des badges nutrition…</p>
          )}
        </CardContent>
      </Card>

      {/* ─── Historique des points ─────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-violet-500" />
            Historique hebdomadaire
          </CardTitle>
        </CardHeader>
        <CardContent>
          <HistoriqueChart data={historiqueData?.items ?? []} />
        </CardContent>
      </Card>
    </div>
  );
}
