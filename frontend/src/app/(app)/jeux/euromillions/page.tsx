"use client";

import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  TableCell,
  TableHead,
  TableRow,
} from "@/composants/ui/table";
import { toast } from "sonner";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirTiragesEuromillions,
  obtenirGrillesEuromillions,
  obtenirStatsEuromillions,
  obtenirNumerosRetard,
  genererGrilleEuromillions,
  creerGrilleEuromillions,
} from "@/bibliotheque/api/jeux";
import type {
  TirageEuromillions,
  GrilleEuromillions,
  StatsEuromillions,
  NumeroRetard,
} from "@/types/jeux";
import { HeatmapNumeros } from "@/composants/jeux/heatmap-numeros";
import { GenerateurGrille } from "@/composants/jeux/generateur-grille";
import { BacktestEuromillionsVue } from "@/composants/jeux/backtest-euromillions-vue";
import { TableauEuromillionsExpert } from "@/composants/jeux/tableau-euromillions-expert";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { PageLoterie, NumeroBoule } from "@/composants/jeux/page-loterie";
import { formaterDate, parseListeNumeros } from "@/composants/jeux/helpers-loterie";

export default function EuromillionsPage() {
  const { user } = utiliserAuth();
  const search = useSearchParams();
  const userIdNumerique = user?.id != null && Number.isFinite(Number(user.id)) ? Number(user.id) : undefined;

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

  const mutationEnregistrer = utiliserMutation(
    () => creerGrilleEuromillions(numerosPrefill, etoilesPrefill, true),
    {
      onSuccess: () => toast.success("Grille enregistrée"),
      onError: () => toast.error("Impossible d'enregistrer la grille"),
    }
  );

  const retardNumeros = retard.filter((n) => n.type_numero === "principal");
  const retardEtoiles = retard.filter((n) => n.type_numero === "etoile");

  const donneesExportTirages = useMemo(
    () =>
      tirages.map((tirage) => ({
        date: formaterDate(tirage.date_tirage),
        numeros: tirage.numeros.join(" - "),
        etoiles: tirage.etoiles.join(" - "),
        jackpot_euros: tirage.jackpot_euros ?? "",
        gagnants_rang1: tirage.gagnants_rang1 ?? "",
      })),
    [tirages]
  );

  return (
    <PageLoterie
      titre="Euromillions"
      emoji="⭐"
      nomJeu="euromillions"
      maxNumeroPrincipal={50}
      colonnesHeatmap={10}
      donneesExport={donneesExportTirages}
      fichierExport="euromillions-tirages.csv"
      stats={stats}
      chargementStats={chStats}
      retardPrincipal={retardNumeros}
      tirages={tirages}
      chargementTirages={chTirages}
      grilles={grilles}
      chargementGrilles={chGrilles}
      userId={userIdNumerique}
      badges={
        <div className="flex gap-2 mt-2 flex-wrap">
          <Badge>Mardi</Badge>
          <Badge>Vendredi</Badge>
          <Badge variant="outline">2,50 € / grille</Badge>
          <Badge variant="outline">Jackpot : 1/139 M</Badge>
        </div>
      }
      expertViewSlot={<TableauEuromillionsExpert />}
      generateurSlot={
        <GenerateurGrille
          typeJeu="euromillions"
          genererFn={genererGrilleEuromillions}
          labelSpecial="Étoiles"
        />
      }
      prefillSlot={
        prefillDisponible ? (
          <Card className="border-emerald-300">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Pré-remplissage rapide d{"'"}une grille</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-1 items-center">
                {numerosPrefill.map((n) => (
                  <NumeroBoule key={n} numero={n} />
                ))}
                <span className="mx-2 text-muted-foreground">|</span>
                {etoilesPrefill.map((n) => (
                  <NumeroBoule key={`e-${n}`} numero={n} variant="secondary" />
                ))}
              </div>
              <Button
                size="sm"
                onClick={() => mutationEnregistrer.mutate(undefined)}
                disabled={mutationEnregistrer.isPending}
              >
                {mutationEnregistrer.isPending ? "Enregistrement..." : "Enregistrer cette grille"}
              </Button>
            </CardContent>
          </Card>
        ) : undefined
      }
      heatmapExtraSlot={
        stats ? (
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
        ) : undefined
      }
      backtestExtraSlot={(data) => <BacktestEuromillionsVue data={data} />}
      tiragesHeaderSlot={
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Numéros</TableHead>
          <TableHead>Étoiles</TableHead>
          <TableHead className="text-right">Jackpot</TableHead>
        </TableRow>
      }
      tiragesBodySlot={
        <>
          {tirages.map((t) => (
            <TableRow key={t.id}>
              <TableCell>{formaterDate(t.date_tirage)}</TableCell>
              <TableCell>
                <div className="flex gap-1">
                  {t.numeros.map((n, i) => (
                    <NumeroBoule key={i} numero={n} />
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex gap-1">
                  {t.etoiles.map((e, i) => (
                    <NumeroBoule key={i} numero={e} variant="secondary" />
                  ))}
                </div>
              </TableCell>
              <TableCell className="text-right">
                {t.jackpot_euros ? `${(t.jackpot_euros / 1_000_000).toFixed(0)} M€` : "-"}
              </TableCell>
            </TableRow>
          ))}
        </>
      }
      grillesHeaderSlot={
        <TableRow>
          <TableHead>Numéros</TableHead>
          <TableHead>Étoiles</TableHead>
          <TableHead>Source</TableHead>
          <TableHead>Type</TableHead>
          <TableHead className="text-right">Mise</TableHead>
        </TableRow>
      }
      grillesBodySlot={
        <>
          {grilles.map((g) => (
            <TableRow key={g.id}>
              <TableCell>
                <div className="flex gap-1">
                  {g.numeros.map((n, i) => (
                    <NumeroBoule key={i} numero={n} size="sm" />
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex gap-1">
                  {g.etoiles.map((e, i) => (
                    <NumeroBoule key={i} numero={e} variant="secondary" size="sm" />
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
        </>
      }
    />
  );
}
