// ═══════════════════════════════════════════════════════════
// Performance Jeux — KPIs, ROI mensuel, Breakdown, Résumé IA
// ═══════════════════════════════════════════════════════════

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirPerformance, obtenirResumeMensuel, obtenirPerformanceConfiance } from "@/bibliotheque/api/jeux";
import type { PerformanceJeux, ResumeMensuel } from "@/types/jeux";
import dynamic from "next/dynamic";

const ComposedChart = dynamic(
  () => import("recharts").then((m) => {
    const { ComposedChart: CC, Line, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Legend } = m;
    return function GraphiqueROIMensuel({ data }: { data: { mois: string; roi: number; nb_paris: number; benefice: number }[] }) {
      if (data.length < 2) return <p className="text-sm text-muted-foreground py-6 text-center">Pas encore assez de données</p>;
      return (
        <ResponsiveContainer width="100%" height={260}>
          <CC data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <XAxis dataKey="mois" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="roi" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
            <YAxis yAxisId="paris" orientation="right" tick={{ fontSize: 11 }} />
            <Tooltip formatter={(val, name) => name === "roi" ? [`${Number(val).toFixed(1)}%`, "ROI"] : [val, "Paris"]} />
            <Legend />
            <ReferenceLine yAxisId="roi" y={0} stroke="hsl(0, 0%, 60%)" strokeDasharray="3 3" />
            <Bar yAxisId="paris" dataKey="nb_paris" fill="hsl(220, 70%, 85%)" name="Nb paris" />
            <Line yAxisId="roi" type="monotone" dataKey="roi" stroke="hsl(210, 70%, 50%)" strokeWidth={2} dot={{ r: 3 }} name="ROI %" />
          </CC>
        </ResponsiveContainer>
      );
    };
  }),
  { ssr: false }
);

const BarChartHorizontal = dynamic(
  () => import("recharts").then((m) => {
    const { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } = m;
    return function BreakdownBar({ data, dataKey, label }: { data: { nom: string; roi: number; nb_paris: number }[]; dataKey: string; label: string }) {
      if (data.length === 0) return <p className="text-sm text-muted-foreground text-center py-4">Aucune donnée</p>;
      return (
        <ResponsiveContainer width="100%" height={Math.max(120, data.length * 40)}>
          <BarChart data={data} layout="vertical" margin={{ top: 0, right: 10, left: 60, bottom: 0 }}>
            <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="nom" tick={{ fontSize: 11 }} width={60} />
            <Tooltip formatter={(val) => [`${Number(val).toFixed(1)}%`, label]} />
            <Bar dataKey={dataKey} fill="hsl(210, 70%, 50%)" radius={3} />
          </BarChart>
        </ResponsiveContainer>
      );
    };
  }),
  { ssr: false }
);

export default function PerformancePage() {
  const { data: perf, isLoading: chPerf } = utiliserRequete<PerformanceJeux>(
    ["jeux", "performance"],
    () => obtenirPerformance()
  );

  const { data: confiance } = utiliserRequete(
    ["jeux", "performance-confiance"],
    () => obtenirPerformanceConfiance()
  );

  const today = new Date();
  const afficherResume = today.getDate() >= 28;
  const moisCourant = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;

  const { data: resume, isLoading: chResume } = utiliserRequete<ResumeMensuel>(
    ["jeux", "resume-mensuel", moisCourant],
    () => obtenirResumeMensuel(moisCourant),
    { enabled: afficherResume }
  );

  if (chPerf) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  const parChampionnat = perf ? Object.entries(perf.par_championnat ?? {}).map(([nom, vals]) => ({
    nom,
    roi: (vals as Record<string, number>).roi ?? 0,
    nb_paris: (vals as Record<string, number>).nb_paris ?? 0,
  })) : [];

  const parType = perf ? Object.entries(perf.par_type_pari ?? {}).map(([nom, vals]) => ({
    nom,
    roi: (vals as Record<string, number>).roi ?? 0,
    nb_paris: (vals as Record<string, number>).nb_paris ?? 0,
  })) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📊 Performance</h1>
        <p className="text-muted-foreground">Analyse complète de vos paris</p>
      </div>

      {/* KPIs globaux */}
      {perf && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-4 text-center">
              <p className={`text-2xl font-bold ${perf.roi >= 0 ? "text-green-600" : "text-red-600"}`}>
                {perf.roi >= 0 ? "+" : ""}{perf.roi.toFixed(1)}%
              </p>
              <p className="text-xs text-muted-foreground">ROI global</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className={`text-2xl font-bold ${perf.benefice >= 0 ? "text-green-600" : "text-red-600"}`}>
                {perf.benefice >= 0 ? "+" : ""}{perf.benefice.toFixed(0)}€
              </p>
              <p className="text-xs text-muted-foreground">Bénéfice total</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{(perf.taux_reussite * 100).toFixed(0)}%</p>
              <p className="text-xs text-muted-foreground">Taux réussite</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{perf.nb_paris}</p>
              <p className="text-xs text-muted-foreground">Total paris</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Séries & records */}
      {perf && (
        <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
          <Card>
            <CardContent className="pt-3 text-center">
              <p className="text-lg font-bold text-green-600">{perf.serie_gagnante_max}</p>
              <p className="text-xs text-muted-foreground">Série gagnante max</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-3 text-center">
              <p className="text-lg font-bold text-red-600">{perf.serie_perdante_max}</p>
              <p className="text-xs text-muted-foreground">Série perdante max</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-3 text-center">
              <p className="text-sm font-bold truncate">{perf.meilleur_mois ?? "—"}</p>
              <p className="text-xs text-muted-foreground">Meilleur mois</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-3 text-center">
              <p className="text-sm font-bold truncate">{perf.pire_mois ?? "—"}</p>
              <p className="text-xs text-muted-foreground">Pire mois</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Graphique ROI mensuel */}
      {perf?.par_mois && perf.par_mois.length > 0 && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">ROI mensuel</CardTitle></CardHeader>
          <CardContent>
            <ComposedChart data={perf.par_mois} />
          </CardContent>
        </Card>
      )}

      {/* Breakdowns */}
      <div className="grid gap-4 md:grid-cols-2">
        {parChampionnat.length > 0 && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Par championnat</CardTitle></CardHeader>
            <CardContent>
              <BarChartHorizontal data={parChampionnat} dataKey="roi" label="ROI" />
            </CardContent>
          </Card>
        )}
        {parType.length > 0 && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Par type de pari</CardTitle></CardHeader>
            <CardContent>
              <BarChartHorizontal data={parType} dataKey="roi" label="ROI" />
            </CardContent>
          </Card>
        )}
      </div>

      {/* Taux de réussite par confiance IA */}
      {confiance && confiance.total > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Taux de réussite par confiance IA</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {confiance.tranches.map((t) => (
                <div key={t.tranche} className="text-center rounded-md border p-3">
                  <p className="text-lg font-bold" style={{ color: t.taux >= 60 ? "hsl(142,70%,45%)" : t.taux >= 40 ? "hsl(45,80%,50%)" : "hsl(0,70%,50%)" }}>
                    {t.taux}%
                  </p>
                  <p className="text-xs text-muted-foreground font-medium">Confiance {t.tranche}</p>
                  <p className="text-xs text-muted-foreground">{t.gagnes}/{t.nb} paris</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Résumé IA mensuel (fin de mois uniquement) */}
      {afficherResume && (
        <div>
          {chResume ? (
            <Skeleton className="h-40" />
          ) : resume ? (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  🤖 Résumé IA — {resume.mois}
                  <Badge variant="secondary">Mensuel</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm">{resume.analyse}</p>
                <div className="grid gap-3 sm:grid-cols-2">
                  {resume.points_forts.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-green-600 mb-1">✅ Points forts</p>
                      <ul className="text-sm list-disc pl-5 space-y-1">
                        {resume.points_forts.map((p, i) => <li key={i}>{p}</li>)}
                      </ul>
                    </div>
                  )}
                  {resume.points_faibles.length > 0 && (
                    <div>
                      <p className="text-xs font-semibold text-red-600 mb-1">⚠️ Points faibles</p>
                      <ul className="text-sm list-disc pl-5 space-y-1">
                        {resume.points_faibles.map((p, i) => <li key={i}>{p}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
                {resume.recommandations.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold mb-1">💡 Recommandations</p>
                    <ul className="text-sm list-disc pl-5">
                      {resume.recommandations.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  </div>
                )}
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Les analyses IA sont indicatives. Jouez de manière responsable.
                </p>
              </CardContent>
            </Card>
          ) : null}
        </div>
      )}
    </div>
  );
}
