"use client";

/**
 * Composant partagé pour les pages de loterie (Loto, Euromillions).
 *
 * Gère la structure commune: header, tabs, heatmap, backtest, tables.
 * Les parties spécifiques à chaque jeu sont injectées via des slots (ReactNode).
 */

import { type ReactNode, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { BoutonExportCsv } from "@/composants/ui/bouton-export-csv";
import {
  Table,
  TableBody,
  TableHeader,
} from "@/composants/ui/table";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirBacktest } from "@/bibliotheque/api/jeux";
import type { NumeroRetard, BacktestResultat } from "@/types/jeux";
import { HeatmapNumeros } from "@/composants/jeux/heatmap-numeros";
import { BacktestResultatCard } from "@/composants/jeux/backtest-resultat";
import { StatsPersonnelles } from "@/composants/jeux/stats-personnelles";
import { TooltipProvider } from "@/composants/ui/tooltip";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";

// ═══════════════════════════════════════════════════════════
// Composant réutilisable pour les boules de numéros
// ═══════════════════════════════════════════════════════════

export function NumeroBoule({
  numero,
  variant = "primary",
  size = "md",
}: {
  numero: number;
  variant?: "primary" | "secondary" | "highlight";
  size?: "sm" | "md" | "lg";
}) {
  const classes = {
    primary: "bg-primary text-primary-foreground",
    secondary: "bg-yellow-500 text-white",
    highlight: "bg-orange-400 text-white",
  };
  const sizes = {
    sm: "h-7 w-7 text-xs",
    md: "h-8 w-8 text-sm",
    lg: "h-12 w-12 text-lg",
  };
  return (
    <span
      className={`inline-flex items-center justify-center rounded-full font-bold ${classes[variant]} ${sizes[size]}`}
    >
      {numero}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════
// Props
// ═══════════════════════════════════════════════════════════

export interface PageLoterieProps {
  // Config
  titre: string;
  emoji: string;
  nomJeu: "loto" | "euromillions";
  maxNumeroPrincipal: number;
  colonnesHeatmap: number;

  // Export
  donneesExport: Record<string, string | number | boolean | null | undefined>[];
  fichierExport: string;

  // Data
  stats: { frequences_numeros: Record<number, number>; total_tirages: number } | undefined;
  chargementStats: boolean;
  retardPrincipal: NumeroRetard[];
  tirages: unknown[];
  chargementTirages: boolean;
  grilles: unknown[];
  chargementGrilles: boolean;

  // Auth
  userId?: number;

  // Slots
  badges?: ReactNode;
  prefillSlot?: ReactNode;
  expertViewSlot: ReactNode;
  generateurSlot: ReactNode;
  heatmapExtraSlot?: ReactNode;
  retardSlot?: ReactNode;
  extraComponentsSlot?: ReactNode;
  backtestExtraSlot?: (data: BacktestResultat | undefined) => ReactNode;
  tiragesHeaderSlot: ReactNode;
  tiragesBodySlot: ReactNode;
  grillesHeaderSlot: ReactNode;
  grillesBodySlot: ReactNode;
}

// ═══════════════════════════════════════════════════════════
// Composant
// ═══════════════════════════════════════════════════════════

export function PageLoterie({
  titre,
  emoji,
  nomJeu,
  maxNumeroPrincipal,
  colonnesHeatmap,
  donneesExport,
  fichierExport,
  stats,
  chargementStats,
  retardPrincipal,
  tirages,
  chargementTirages,
  grilles,
  chargementGrilles,
  userId,
  badges,
  prefillSlot,
  expertViewSlot,
  generateurSlot,
  heatmapExtraSlot,
  retardSlot,
  extraComponentsSlot,
  backtestExtraSlot,
  tiragesHeaderSlot,
  tiragesBodySlot,
  grillesHeaderSlot,
  grillesBodySlot,
}: PageLoterieProps) {
  const [showBacktest, setShowBacktest] = useState(false);
  const [modeVue, setModeVue] = useState<"simple" | "expert">("simple");

  const { data: backtest, isLoading: chBacktest } = utiliserRequete<BacktestResultat>(
    ["jeux", `backtest-${nomJeu}`],
    () => obtenirBacktest(nomJeu, 2.0),
    { enabled: showBacktest }
  );

  const labelHeatmap = useMemo(() => {
    if (!stats) return "";
    return `${nomJeu === "loto" ? "Loto — " : ""}${stats.total_tirages} tirages analysés`;
  }, [stats, nomJeu]);

  return (
    <TooltipProvider>
      <div className="space-y-6">
        {/* ── Header ── */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              {emoji} {titre}
            </h1>
            {badges}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <BoutonExportCsv
              data={donneesExport}
              filename={fichierExport}
              label="Exporter CSV"
            />
            <Button
              variant={modeVue === "simple" ? "default" : "outline"}
              size="sm"
              onClick={() => setModeVue("simple")}
            >
              🎯 Simple
            </Button>
            <Button
              variant={modeVue === "expert" ? "default" : "outline"}
              size="sm"
              onClick={() => setModeVue("expert")}
            >
              📊 Expert
            </Button>
          </div>
        </div>

        {/* ── Tabs ── */}
        <Tabs defaultValue="grilles">
          <TabsList>
            <TabsTrigger value="grilles">
              {emoji} Grilles
            </TabsTrigger>
            <TabsTrigger value="stats">📊 Mes Stats</TabsTrigger>
          </TabsList>

          <TabsContent value="grilles" className="space-y-6 mt-6">
            {modeVue === "expert" ? (
              expertViewSlot
            ) : (
              <>
                {prefillSlot}

                {/* Heatmap fréquences principales */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Fréquences des numéros</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {chargementStats ? (
                      <Skeleton className="h-40 w-full" />
                    ) : stats ? (
                      <HeatmapNumeros
                        frequences={stats.frequences_numeros}
                        maxNumero={maxNumeroPrincipal}
                        colonnes={colonnesHeatmap}
                        numerosRetard={retardPrincipal}
                        label={labelHeatmap}
                      />
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        Aucune statistique disponible
                      </p>
                    )}
                  </CardContent>
                </Card>

                {heatmapExtraSlot}
                {retardSlot}
                {generateurSlot}
                {extraComponentsSlot}

                {/* Backtest */}
                <div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowBacktest(!showBacktest)}
                    className="mb-3"
                  >
                    📊 Backtest {titre} {showBacktest ? "▲" : "▼"}
                  </Button>
                  {showBacktest && (
                    <div className="space-y-3">
                      <BacktestResultatCard data={backtest} isLoading={chBacktest} />
                      {backtestExtraSlot?.(backtest)}
                    </div>
                  )}
                </div>

                {/* Derniers tirages */}
                <Card>
                  <CardHeader>
                    <CardTitle>Derniers tirages</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {chargementTirages ? (
                      <div className="space-y-2">
                        {Array.from({ length: 4 }).map((_, i) => (
                          <Skeleton key={i} className="h-10 w-full" />
                        ))}
                      </div>
                    ) : tirages.length === 0 ? (
                      <p className="text-center py-8 text-muted-foreground">
                        Aucun tirage enregistré
                      </p>
                    ) : (
                      <Table>
                        <TableHeader>{tiragesHeaderSlot}</TableHeader>
                        <TableBody>{tiragesBodySlot}</TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>

                {/* Mes grilles */}
                <Card>
                  <CardHeader>
                    <CardTitle>Mes grilles</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {chargementGrilles ? (
                      <div className="space-y-2">
                        {Array.from({ length: 3 }).map((_, i) => (
                          <Skeleton key={i} className="h-10 w-full" />
                        ))}
                      </div>
                    ) : grilles.length === 0 ? (
                      <p className="text-center py-8 text-muted-foreground">
                        Aucune grille enregistrée
                      </p>
                    ) : (
                      <Table>
                        <TableHeader>{grillesHeaderSlot}</TableHeader>
                        <TableBody>{grillesBodySlot}</TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          <TabsContent value="stats" className="mt-6">
            {userId && <StatsPersonnelles userId={userId} />}
          </TabsContent>
        </Tabs>
      </div>
    </TooltipProvider>
  );
}
