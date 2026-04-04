"use client";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirTiragesEuromillions,
  obtenirGrillesEuromillions,
  obtenirStatsEuromillions,
  obtenirNumerosRetard,
  genererGrilleEuromillions,
  obtenirBacktest,
  creerGrilleEuromillions,
} from "@/bibliotheque/api/jeux";
import type {
  TirageEuromillions,
  GrilleEuromillions,
  StatsEuromillions,
  NumeroRetard,
  BacktestResultat,
} from "@/types/jeux";
import { HeatmapNumeros } from "@/composants/jeux/heatmap-numeros";
import { GenerateurGrille } from "@/composants/jeux/generateur-grille";
import { BacktestResultatCard } from "@/composants/jeux/backtest-resultat";
import { BacktestEuromillionsVue } from "@/composants/jeux/backtest-euromillions-vue";
import { TableauEuromillionsExpert } from "@/composants/jeux/tableau-euromillions-expert";
import { StatsPersonnelles } from "@/composants/jeux/stats-personnelles";
import { TooltipProvider } from "@/composants/ui/tooltip";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserAuth } from "@/crochets/utiliser-auth";

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function parseListeNumeros(raw: string | null, min: number, max: number, attendu: number): number[] {
  if (!raw) return [];
  const nums = raw
    .split(",")
    .map((v) => Number(v.trim()))
    .filter((n) => Number.isInteger(n) && n >= min && n <= max);
  const uniq = Array.from(new Set(nums)).sort((a, b) => a - b);
  return uniq.length === attendu ? uniq : [];
}

export default function EuromillionsPage() {
  const [showBacktest, setShowBacktest] = useState(false);
  const [modeVue, setModeVue] = useState<"simple" | "expert">("simple");
  const { user } = utiliserAuth();
  const search = useSearchParams();

  const numerosPrefill = useMemo(
    () => parseListeNumeros(search.get("numeros"), 1, 50, 5),
    [search]
  );
  const etoilesPrefill = useMemo(
    () => parseListeNumeros(search.get("etoiles"), 1, 12, 2),
    [search]
  );
  const prefillDisponible = numerosPrefill.length === 5 && etoilesPrefill.length === 2;

  const { data: tirages = [], isLoading: chTirages } = utiliserRequete<TirageEuromillions[]>(
    ["jeux", "euromillions", "tirages"],
    obtenirTiragesEuromillions
  );

  const { data: grilles = [], isLoading: chGrilles } = utiliserRequete<GrilleEuromillions[]>(
    ["jeux", "euromillions", "grilles"],
    obtenirGrillesEuromillions
  );

  const { data: stats, isLoading: chStats } = utiliserRequete<StatsEuromillions>(
    ["jeux", "euromillions", "stats"],
    obtenirStatsEuromillions
  );

  const { data: retard = [] } = utiliserRequete<NumeroRetard[]>(
    ["jeux", "euromillions", "retard"],
    () => obtenirNumerosRetard(2.0)
  );

  const { data: backtest, isLoading: chBacktest } = utiliserRequete<BacktestResultat>(
    ["jeux", "backtest-euromillions"],
    () => obtenirBacktest("euromillions", 2.0),
    { enabled: showBacktest }
  );

  const mutationEnregistrer = utiliserMutation(
    () => creerGrilleEuromillions(numerosPrefill, etoilesPrefill, true),
    {
      onSuccess: () => toast.success("Grille enregistrée"),
      onError: () => toast.error("Impossible d'enregistrer la grille"),
    }
  );

  const retardNumeros = retard.filter((n) => n.type_numero === "principal");
  const retardEtoiles = retard.filter((n) => n.type_numero === "etoile");

  return (
    <TooltipProvider>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">⭐ Euromillions</h1>
            <div className="flex gap-2 mt-2 flex-wrap">
              <Badge>Mardi</Badge>
              <Badge>Vendredi</Badge>
              <Badge variant="outline">2,50 € / grille</Badge>
              <Badge variant="outline">Jackpot : 1/139 M</Badge>
            </div>
          </div>
          <div className="flex items-center gap-2">
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

        <Tabs defaultValue="grilles">
          <TabsList>
            <TabsTrigger value="grilles">⭐ Grilles</TabsTrigger>
            <TabsTrigger value="stats">📊 Mes Stats</TabsTrigger>
          </TabsList>

          <TabsContent value="grilles" className="space-y-6 mt-6">
            {modeVue === "expert" ? (
              <TableauEuromillionsExpert />
            ) : (
              <>

        {prefillDisponible && (
          <Card className="border-emerald-300">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Pré-remplissage rapide d'une grille</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-1 items-center">
                {numerosPrefill.map((n) => (
                  <span key={n} className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">
                    {n}
                  </span>
                ))}
                <span className="mx-2 text-muted-foreground">|</span>
                {etoilesPrefill.map((n) => (
                  <span key={`e-${n}`} className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-yellow-500 text-white text-sm font-bold">
                    {n}
                  </span>
                ))}
              </div>
              <Button size="sm" onClick={() => mutationEnregistrer.mutate(undefined)} disabled={mutationEnregistrer.isPending}>
                {mutationEnregistrer.isPending ? "Enregistrement..." : "Enregistrer cette grille"}
              </Button>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Fréquences — Numéros 1-50</CardTitle>
          </CardHeader>
          <CardContent>
            {chStats ? (
              <Skeleton className="h-40 w-full" />
            ) : stats ? (
              <HeatmapNumeros
                frequences={stats.frequences_numeros}
                maxNumero={50}
                colonnes={10}
                numerosRetard={retardNumeros}
                label={`${stats.total_tirages} tirages analysés`}
              />
            ) : (
              <p className="text-sm text-muted-foreground">Aucune statistique disponible</p>
            )}
          </CardContent>
        </Card>

        {stats && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Fréquences — Étoiles 1-12</CardTitle>
            </CardHeader>
            <CardContent>
              <HeatmapNumeros
                frequences={stats.frequences_etoiles}
                maxNumero={12}
                colonnes={6}
                numerosRetard={retardEtoiles}
                label="Étoiles"
              />
            </CardContent>
          </Card>
        )}

        <GenerateurGrille
          typeJeu="euromillions"
          genererFn={genererGrilleEuromillions}
          labelSpecial="Étoiles"
        />

        <div>
          <Button variant="outline" size="sm" onClick={() => setShowBacktest(!showBacktest)} className="mb-3">
            📊 Backtest Euromillions {showBacktest ? "▲" : "▼"}
          </Button>
          {showBacktest && (
            <div className="space-y-3">
              <BacktestResultatCard data={backtest} isLoading={chBacktest} />
              <BacktestEuromillionsVue data={backtest} />
            </div>
          )}
        </div>

        <Card>
          <CardHeader><CardTitle>Derniers tirages</CardTitle></CardHeader>
          <CardContent>
            {chTirages ? (
              <div className="space-y-2">
                {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : tirages.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">Aucun tirage enregistré</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Numéros</TableHead>
                    <TableHead>Étoiles</TableHead>
                    <TableHead className="text-right">Jackpot</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tirages.map((t) => (
                    <TableRow key={t.id}>
                      <TableCell>{formaterDate(t.date_tirage)}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {t.numeros.map((n, i) => (
                            <span key={i} className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">
                              {n}
                            </span>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {t.etoiles.map((e, i) => (
                            <span key={i} className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-yellow-500 text-white text-sm font-bold">
                              {e}
                            </span>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        {t.jackpot_euros ? `${(t.jackpot_euros / 1_000_000).toFixed(0)} M€` : "-"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Mes grilles</CardTitle></CardHeader>
          <CardContent>
            {chGrilles ? (
              <div className="space-y-2">
                {Array.from({ length: 2 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
              </div>
            ) : grilles.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">Aucune grille enregistrée</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Numéros</TableHead>
                    <TableHead>Étoiles</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="text-right">Mise</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {grilles.map((g) => (
                    <TableRow key={g.id}>
                      <TableCell>
                        <div className="flex gap-1">
                          {g.numeros.map((n, i) => (
                            <span key={i} className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">
                              {n}
                            </span>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {g.etoiles.map((e, i) => (
                            <span key={i} className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-yellow-500 text-white text-xs font-bold">
                              {e}
                            </span>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell className="text-xs">{g.source_prediction ?? "Manuel"}</TableCell>
                      <TableCell>
                        <Badge variant={g.est_virtuelle ? "secondary" : "default"}>
                          {g.est_virtuelle ? "Virtuelle" : "Réelle"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">{g.mise.toFixed(2)} €</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
              </>
            )}
          </TabsContent>

          <TabsContent value="stats" className="mt-6">
            {user && <StatsPersonnelles userId={user.id} />}
          </TabsContent>
        </Tabs>
      </div>
    </TooltipProvider>
  );
}
