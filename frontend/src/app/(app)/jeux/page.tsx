// ═══════════════════════════════════════════════════════════
// Hub Jeux — Dashboard avec budget, opportunités, IA, KPIs
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { Trophy, Ticket, Star, TrendingUp, AlertTriangle, Shield, Bell, ScanLine } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirDashboardJeux } from "@/bibliotheque/api/jeux";
import type { DashboardJeux, ValueBet, SerieJeux, NumeroRetard } from "@/types/jeux";
import { useRouter } from "next/navigation";

function couleurBudget(pct: number) {
  if (pct >= 90) return "bg-red-500";
  if (pct >= 75) return "bg-orange-400";
  if (pct >= 50) return "bg-yellow-400";
  return "bg-green-500";
}

function BandeauBudget({ budget }: { budget: DashboardJeux["budget"] }) {
  const pct = Math.min(budget.pourcentage_utilise, 100);
  return (
    <Card>
      <CardContent className="pt-4 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Budget mensuel</span>
          <span className="text-sm text-muted-foreground">
            {budget.mises_cumulees.toFixed(0)}€ / {budget.limite.toFixed(0)}€
          </span>
        </div>
        <div className="h-3 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${couleurBudget(pct)}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Reste : {budget.reste_disponible.toFixed(0)}€</span>
          {budget.cooldown_actif && (
            <Badge variant="secondary">⏸️ Période de réflexion</Badge>
          )}
          {budget.auto_exclusion_jusqu_a && (
            <Badge variant="destructive">
              🚫 Exclusion jusqu&apos;au{" "}
              {new Date(budget.auto_exclusion_jusqu_a).toLocaleDateString("fr-FR")}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function SectionOpportunites({
  valueBets,
  series,
  lotoRetard,
}: {
  valueBets: ValueBet[];
  series: SerieJeux[];
  lotoRetard: NumeroRetard[];
}) {
  const hasContent = valueBets.length > 0 || series.length > 0 || lotoRetard.length > 0;
  if (!hasContent) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          Aucune opportunité aujourd&apos;hui
        </CardContent>
      </Card>
    );
  }
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">🎯 Opportunités du jour</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {valueBets.slice(0, 3).map((vb) => (
          <Link key={vb.match_id} href="/jeux/paris">
            <Card className="hover:bg-accent/50 transition-colors cursor-pointer h-full">
              <CardContent className="pt-4 space-y-1">
                <p className="font-medium text-sm truncate">
                  {vb.equipe_domicile} vs {vb.equipe_exterieur}
                </p>
                <div className="flex items-center gap-2">
                  <Badge variant="default">💰 Value +{vb.edge_pct.toFixed(0)}%</Badge>
                  <span className="text-xs text-muted-foreground">cote {vb.cote_bookmaker.toFixed(2)}</span>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
        {series.slice(0, 2).map((s) => (
          <Link key={s.id} href={s.type_jeu === "paris" ? "/jeux/paris" : "/jeux/loto"}>
            <Card className="hover:bg-accent/50 transition-colors cursor-pointer h-full">
              <CardContent className="pt-4 space-y-1">
                <p className="font-medium text-sm truncate">
                  🔥 {s.marche} {s.championnat ? `(${s.championnat})` : ""}
                </p>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">Série {s.serie_actuelle}</Badge>
                  <span className="text-xs text-muted-foreground">
                    value {s.value.toFixed(1)}
                  </span>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

function SectionIA({ analyse }: { analyse?: DashboardJeux["analyse_ia"] }) {
  if (!analyse) return null;
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          🤖 L&apos;IA résume
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm">{analyse.resume}</p>
        {analyse.points_cles.length > 0 && (
          <ul className="text-sm list-disc pl-5 space-y-1">
            {analyse.points_cles.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        )}
        {analyse.recommandations.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-muted-foreground mb-1">Recommandations</p>
            <ul className="text-sm list-disc pl-5 space-y-1">
              {analyse.recommandations.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
        )}
        <p className="text-xs text-muted-foreground flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          {analyse.avertissement}
        </p>
      </CardContent>
    </Card>
  );
}

export default function PageJeux() {
  const router = useRouter();
  const { data: dashboard, isLoading } = utiliserRequete<DashboardJeux>(
    ["jeux", "dashboard"],
    obtenirDashboardJeux
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-20 w-full" />
        <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🎮 Jeux</h1>
          <p className="text-muted-foreground">
            Paris sportifs, tirages et analyse IA
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/jeux/ocr-ticket">
            <Badge variant="outline" className="cursor-pointer gap-1">
              <ScanLine className="h-3 w-3" /> OCR ticket
            </Badge>
          </Link>
          <Link href="/jeux/responsable">
            <Badge variant="outline" className="cursor-pointer gap-1">
              <Shield className="h-3 w-3" /> Jeu responsable
            </Badge>
          </Link>
          <Link href="/jeux/performance">
            <Badge variant="outline" className="cursor-pointer gap-1">
              <TrendingUp className="h-3 w-3" /> Performance
            </Badge>
          </Link>
        </div>
      </div>

      {/* Bandeau budget */}
      {dashboard?.budget && <BandeauBudget budget={dashboard.budget} />}

      {/* Opportunités du jour */}
      {dashboard && (
        <SectionOpportunites
          valueBets={dashboard.value_bets ?? []}
          series={dashboard.opportunites ?? []}
          lotoRetard={dashboard.loto_retard ?? []}
        />
      )}

      {/* Section IA */}
      <SectionIA analyse={dashboard?.analyse_ia} />

      {/* KPIs compacts */}
      {dashboard?.kpis && (
        <div className="grid gap-3 grid-cols-2 md:grid-cols-4">
          <Card>
            <CardContent className="pt-4 text-center">
              <p className={`text-2xl font-bold ${dashboard.kpis.roi_mois >= 0 ? "text-green-600" : "text-red-600"}`}>
                {dashboard.kpis.roi_mois >= 0 ? "+" : ""}
                {dashboard.kpis.roi_mois.toFixed(1)}%
              </p>
              <p className="text-xs text-muted-foreground">ROI ce mois</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">
                {(dashboard.kpis.taux_reussite_mois * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-muted-foreground">Taux réussite</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className={`text-2xl font-bold ${dashboard.kpis.benefice_mois >= 0 ? "text-green-600" : "text-red-600"}`}>
                {dashboard.kpis.benefice_mois >= 0 ? "+" : ""}
                {dashboard.kpis.benefice_mois.toFixed(0)}€
              </p>
              <p className="text-xs text-muted-foreground">Bénéfice</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{dashboard.kpis.paris_actifs}</p>
              <p className="text-xs text-muted-foreground">Paris actifs</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Navigation par onglets */}
      <Tabs defaultValue="paris" onValueChange={(v) => router.push(`/jeux/${v}`)}>
        <TabsList className="w-full grid grid-cols-3">
          <TabsTrigger value="paris" className="gap-1">
            <Trophy className="h-4 w-4" /> Paris
          </TabsTrigger>
          <TabsTrigger value="loto" className="gap-1">
            <Ticket className="h-4 w-4" /> Loto
          </TabsTrigger>
          <TabsTrigger value="euromillions" className="gap-1">
            <Star className="h-4 w-4" /> Euromillions
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  );
}
