"use client";

import { useState } from "react";
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
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirTiragesEuromillions,
  obtenirGrillesEuromillions,
  obtenirStatsEuromillions,
  obtenirNumerosRetard,
  genererGrilleEuromillions,
  obtenirBacktest,
} from "@/bibliotheque/api/jeux";
import type { TirageEuromillions, GrilleEuromillions, StatsEuromillions, NumeroRetard, BacktestResultat } from "@/types/jeux";
import { HeatmapNumeros } from "@/composants/jeux/heatmap-numeros";
import { GenerateurGrille } from "@/composants/jeux/generateur-grille";
import { BacktestResultatCard } from "@/composants/jeux/backtest-resultat";
import { TooltipProvider } from "@/composants/ui/tooltip";

function formaterDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short", year: "numeric" });
}

export default function EuromillionsPage() {
  const [showBacktest, setShowBacktest] = useState(false);

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

  const { data: retard = [], isLoading: chRetard } = utiliserRequete<NumeroRetard[]>(
    ["jeux", "euromillions", "retard"],
    () => obtenirNumerosRetard(2.0)
  );

  const { data: backtest, isLoading: chBacktest } = utiliserRequete<BacktestResultat>(
    ["jeux", "backtest-euromillions"],
    () => obtenirBacktest("euromillions", 2.0),
    { enabled: showBacktest }
  );

  const retardNumeros = retard.filter((n) => n.type_numero === "principal");
  const retardEtoiles = retard.filter((n) => n.type_numero === "etoile");

  return (
    <TooltipProvider>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">⭐ Euromillions</h1>
          <div className="flex gap-2 mt-2">
            <Badge>Mardi</Badge>
            <Badge>Vendredi</Badge>
            <Badge variant="outline">2,50 € / grille</Badge>
            <Badge variant="outline">Jackpot : 1/139 M</Badge>
          </div>
        </div>

        {/* Heatmap numéros principaux */}
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

        {/* Heatmap étoiles */}
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

        {/* Numéros en retard */}
        {(retardNumeros.length > 0 || retardEtoiles.length > 0) && (
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base">Numéros en retard</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {retardNumeros.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Numéros principaux</p>
                  <div className="flex flex-wrap gap-2">
                    {retardNumeros.slice(0, 8).map((n) => (
                      <div key={n.numero} className="flex flex-col items-center gap-0.5">
                        <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-bold">
                          {n.numero}
                          {n.value >= 2.0 && <span className="text-[8px]">🔥</span>}
                        </span>
                        <span className="text-xs text-muted-foreground">{n.value.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {retardEtoiles.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Étoiles</p>
                  <div className="flex flex-wrap gap-2">
                    {retardEtoiles.map((n) => (
                      <div key={n.numero} className="flex flex-col items-center gap-0.5">
                        <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-yellow-500 text-white text-sm font-bold">
                          ⭐{n.numero}
                        </span>
                        <span className="text-xs text-muted-foreground">{n.value.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Générateur */}
        <GenerateurGrille
          typeJeu="euromillions"
          genererFn={genererGrilleEuromillions}
          labelSpecial="Étoiles"
        />

        {/* Backtest */}
        <div>
          <Button variant="outline" size="sm" onClick={() => setShowBacktest(!showBacktest)} className="mb-3">
            📊 Backtest {showBacktest ? "▲" : "▼"}
          </Button>
          {showBacktest && <BacktestResultatCard data={backtest} isLoading={chBacktest} />}
        </div>

        {/* Tirages */}
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

        {/* Mes grilles */}
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
                    <TableHead className="text-right">Gain</TableHead>
                    <TableHead>Rang</TableHead>
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
                      <TableCell className="text-right">{g.gain != null ? `${g.gain.toFixed(2)} €` : "-"}</TableCell>
                      <TableCell>{g.rang != null ? `Rang ${g.rang}` : "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </TooltipProvider>
  );
}

function genererGrilleAleatoire() {
  const nums: number[] = [];
  while (nums.length < 5) {
    const n = Math.floor(Math.random() * NUMEROS_PRINCIPAUX) + 1;
    if (!nums.includes(n)) nums.push(n);
  }
  nums.sort((a, b) => a - b);

  const etoiles: number[] = [];
  while (etoiles.length < 2) {
    const e = Math.floor(Math.random() * ETOILES) + 1;
    if (!etoiles.includes(e)) etoiles.push(e);
  }
  etoiles.sort((a, b) => a - b);

  return { numeros: nums, etoiles };
}

import { useState } from "react";
import { Button } from "@/composants/ui/button";

export default function EuromillionsPage() {
  const [grille, setGrille] = useState(genererGrilleAleatoire);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">⭐ Euromillions</h1>

      <Card>
        <CardHeader>
          <CardTitle>Générateur de grille</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <p className="text-sm text-muted-foreground mb-3">
              5 numéros (1-{NUMEROS_PRINCIPAUX})
            </p>
            <div className="flex gap-2">
              {grille.numeros.map((n, i) => (
                <span
                  key={i}
                  className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground text-lg font-bold"
                >
                  {n}
                </span>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm text-muted-foreground mb-3">
              2 étoiles (1-{ETOILES})
            </p>
            <div className="flex gap-2">
              {grille.etoiles.map((e, i) => (
                <span
                  key={i}
                  className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-yellow-500 text-white text-lg font-bold"
                >
                  ⭐ {e}
                </span>
              ))}
            </div>
          </div>

          <Button onClick={() => setGrille(genererGrilleAleatoire())}>
            🎲 Nouvelle grille
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Informations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="text-center p-4 rounded-lg bg-muted">
              <p className="text-3xl font-bold text-primary">5 + 2</p>
              <p className="text-sm text-muted-foreground mt-1">Numéros à choisir</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted">
              <p className="text-3xl font-bold text-primary">1/139M</p>
              <p className="text-sm text-muted-foreground mt-1">Probabilité jackpot</p>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted">
              <p className="text-3xl font-bold text-primary">13</p>
              <p className="text-sm text-muted-foreground mt-1">Rangs de gains</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Badge>Mardi</Badge>
            <Badge>Vendredi</Badge>
            <Badge variant="outline">2,50 € / grille</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
