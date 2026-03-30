// ═══════════════════════════════════════════════════════════
// Page Jeux — Bankroll Management
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { ArrowRight, TrendingUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { BankrollWidget } from "@/composants/jeux/bankroll-widget";

export default function PageBankroll() {
  const { utilisateur } = utiliserAuth();
  const userId = Number(utilisateur?.id ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Bankroll Management</h1>
          <p className="text-muted-foreground">
            Pilotage du capital de jeu avec Kelly fractionnaire et suivi du risque.
          </p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="gap-1"><TrendingUp className="h-3 w-3" />ROI</Badge>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Objectif</CardTitle>
          <CardDescription>
            Éviter les mises impulsives en suivant une taille de mise proportionnelle au risque réel.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <p>
            La mise recommandée est plafonnée pour protéger la bankroll et limiter la variance.
            Vous pouvez ajuster les hypothèses de cote et d&apos;edge pour simuler différents scénarios.
          </p>
        </CardContent>
      </Card>

      {userId > 0 ? (
        <BankrollWidget userId={userId} />
      ) : (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Impossible de charger la bankroll: utilisateur non identifié.
          </CardContent>
        </Card>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        <Link href="/jeux/performance">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="text-sm font-medium">Performance mensuelle</p>
                <p className="text-xs text-muted-foreground">ROI, séries, breakdowns</p>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>
        <Link href="/jeux/responsable">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="text-sm font-medium">Jeu responsable</p>
                <p className="text-xs text-muted-foreground">Limites, alertes, auto-exclusion</p>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
