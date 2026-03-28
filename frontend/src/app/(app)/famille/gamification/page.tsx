"use client";

import { Award, HeartPulse, Recycle, Trophy } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Progress } from "@/composants/ui/progress";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirPointsFamille, obtenirScoreBienEtre } from "@/bibliotheque/api/tableau-bord";

export default function PageGamificationFamille() {
  const { data: points } = utiliserRequete(["dashboard", "points-famille"], obtenirPointsFamille);
  const { data: score } = utiliserRequete(["dashboard", "score-bienetre"], obtenirScoreBienEtre);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Points famille</h1>
        <p className="text-muted-foreground">
          Gamification sport, alimentation et anti-gaspillage pour suivre la dynamique hebdomadaire.
        </p>
      </div>

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
            <CardTitle className="text-sm text-muted-foreground">Badges</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center gap-2">
            <Award className="h-5 w-5 text-amber-500" />
            <p className="text-3xl font-bold">{points?.badges.length ?? 0}</p>
          </CardContent>
        </Card>
      </div>

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

      <Card>
        <CardHeader>
          <CardTitle>Badges débloqués</CardTitle>
        </CardHeader>
        <CardContent>
          {points?.badges?.length ? (
            <div className="flex flex-wrap gap-2">
              {points.badges.map((badge) => (
                <span key={badge} className="rounded-full border px-3 py-1 text-sm">
                  {badge}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Aucun badge pour le moment.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
