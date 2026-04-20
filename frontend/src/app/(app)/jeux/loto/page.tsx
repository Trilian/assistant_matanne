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
import { Skeleton } from "@/composants/ui/skeleton";
import { toast } from "sonner";
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  listerTirages,
  listerGrilles,
  obtenirStatsLoto,
  obtenirNumerosRetard,
  genererGrilleLoto,
  genererGrilleIAPonderee,
  analyserGrilleJoueur,
} from "@/bibliotheque/api/jeux";
import type { TirageLoto, GrilleLoto, StatsLoto, NumeroRetard } from "@/types/jeux";
import { GenerateurGrille } from "@/composants/jeux/generateur-grille";
import { GrilleIAPonderee } from "@/composants/jeux/grille-ia-ponderee";
import { TableauLotoExpert } from "@/composants/jeux/tableau-loto-expert";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { PageLoterie, NumeroBoule } from "@/composants/jeux/page-loterie";
import { formaterDate, parseListeNumeros } from "@/composants/jeux/helpers-loterie";

export default function LotoPage() {
  const { user } = utiliserAuth();
  const search = useSearchParams();
  const userIdNumerique = user?.id != null && Number.isFinite(Number(user.id)) ? Number(user.id) : undefined;

  const numerosPrefill = useMemo(
    () => parseListeNumeros(search.get("numeros"), 1, 49, 5),
    [search]
  );
  const chancePrefill = useMemo(() => {
    const raw = Number(search.get("chance"));
    if (!Number.isInteger(raw) || raw < 1 || raw > 10) return null;
    return raw;
  }, [search]);

  const { data: tirages = [], isLoading: chargementTirages } = utiliserRequete<TirageLoto[]>(
    ["jeux", "loto", "tirages"],
    listerTirages
  );
  const { data: grilles = [], isLoading: chargementGrilles } = utiliserRequete<GrilleLoto[]>(
    ["jeux", "loto", "grilles"],
    listerGrilles
  );
  const { data: stats, isLoading: chStats } = utiliserRequete<StatsLoto>(
    ["jeux", "loto", "stats"],
    obtenirStatsLoto
  );
  const { data: retard = [], isLoading: chRetard } = utiliserRequete<NumeroRetard[]>(
    ["jeux", "loto", "retard"],
    () => obtenirNumerosRetard(2.0)
  );

  const donneesExportTirages = useMemo(
    () =>
      tirages.map((tirage) => ({
        date: formaterDate(tirage.date_tirage),
        numeros: tirage.numeros.join(" - "),
        numero_chance: tirage.numero_chance ?? "",
        jackpot_euros: tirage.jackpot_euros ?? "",
        gagnants_rang1: tirage.gagnants_rang1 ?? "",
      })),
    [tirages]
  );

  const retardSet = useMemo(() => new Set(retard.map((r) => r.numero)), [retard]);

  return (
    <PageLoterie
      titre="Loto"
      emoji="🎱"
      nomJeu="loto"
      maxNumeroPrincipal={49}
      colonnesHeatmap={7}
      donneesExport={donneesExportTirages}
      fichierExport="loto-tirages.csv"
      stats={stats}
      chargementStats={chStats}
      retardPrincipal={retard}
      tirages={tirages}
      chargementTirages={chargementTirages}
      grilles={grilles}
      chargementGrilles={chargementGrilles}
      userId={userIdNumerique}
      expertViewSlot={<TableauLotoExpert />}
      generateurSlot={<GenerateurGrille typeJeu="loto" genererFn={genererGrilleLoto} />}
      prefillSlot={
        numerosPrefill.length === 5 ? (
          <Card className="border-emerald-300">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Pré-remplissage rapide d{"'"}une grille</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-1.5 items-center">
                {numerosPrefill.map((n) => (
                  <NumeroBoule key={n} numero={n} />
                ))}
                {chancePrefill && (
                  <>
                    <span className="mx-2 text-muted-foreground">|</span>
                    <NumeroBoule numero={chancePrefill} variant="secondary" />
                  </>
                )}
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  const texte = `${numerosPrefill.join(" - ")}${chancePrefill ? ` | Chance ${chancePrefill}` : ""}`;
                  navigator.clipboard.writeText(texte);
                  toast.success("Grille copiée dans le presse-papiers");
                }}
              >
                Copier la grille
              </Button>
            </CardContent>
          </Card>
        ) : undefined
      }
      retardSlot={
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Numéros en retard</CardTitle>
          </CardHeader>
          <CardContent>
            {chRetard ? (
              <Skeleton className="h-24 w-full" />
            ) : retard.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucun numéro en retard notable</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {retard.slice(0, 10).map((n) => (
                  <div key={n.numero} className="flex flex-col items-center gap-0.5">
                    <span className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground text-lg font-bold relative">
                      {n.numero}
                      {n.value >= 2.0 && (
                        <span className="absolute -top-1 -right-0.5 text-xs">🔥</span>
                      )}
                    </span>
                    <span className="text-xs text-muted-foreground">{n.value.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      }
      extraComponentsSlot={
        <GrilleIAPonderee
          onGenerer={async (mode) => {
            try {
              const res = await genererGrilleIAPonderee(mode, false);
              return { numeros: res.numeros, numero_chance: res.numero_chance, mode: res.mode, analyse: res.analyse, confiance: res.confiance };
            } catch (error) {
              toast.error("Erreur lors de la génération IA");
              throw error;
            }
          }}
          onAnalyser={async (numeros, numeroChance) => {
            try {
              return await analyserGrilleJoueur(numeros, numeroChance);
            } catch (error) {
              toast.error("Erreur lors de l'analyse");
              throw error;
            }
          }}
        />
      }
      tiragesHeaderSlot={
        <TableRow>
          <TableHead>Date</TableHead>
          <TableHead>Numéros</TableHead>
          <TableHead>N° Chance</TableHead>
          <TableHead className="text-right">Jackpot</TableHead>
          <TableHead className="text-right">Gagnants rang 1</TableHead>
        </TableRow>
      }
      tiragesBodySlot={
        <>
          {tirages.map((t) => (
            <TableRow key={t.id}>
              <TableCell>{formaterDate(t.date_tirage)}</TableCell>
              <TableCell>
                <div className="flex gap-1.5">
                  {t.numeros.map((n, i) => (
                    <NumeroBoule key={i} numero={n} variant={retardSet.has(n) ? "highlight" : "primary"} />
                  ))}
                </div>
              </TableCell>
              <TableCell>
                {t.numero_chance != null ? (
                  <NumeroBoule numero={t.numero_chance} variant="secondary" />
                ) : "-"}
              </TableCell>
              <TableCell className="text-right">
                {t.jackpot_euros ? `${(t.jackpot_euros / 1_000_000).toFixed(1)} M€` : "-"}
              </TableCell>
              <TableCell className="text-right">{t.gagnants_rang1 ?? "-"}</TableCell>
            </TableRow>
          ))}
        </>
      }
      grillesHeaderSlot={
        <TableRow>
          <TableHead>Tirage</TableHead>
          <TableHead>Numéros</TableHead>
          <TableHead>N° Chance</TableHead>
          <TableHead>Source</TableHead>
          <TableHead>Type</TableHead>
        </TableRow>
      }
      grillesBodySlot={
        <>
          {grilles.map((g) => (
            <TableRow key={g.id}>
              <TableCell>#{g.tirage_id ?? "-"}</TableCell>
              <TableCell>
                <div className="flex gap-1.5">
                  {g.numeros.map((n, i) => (
                    <NumeroBoule key={i} numero={n} size="sm" />
                  ))}
                </div>
              </TableCell>
              <TableCell>
                {g.numero_chance != null ? (
                  <NumeroBoule numero={g.numero_chance} variant="secondary" />
                ) : "-"}
              </TableCell>
              <TableCell>{g.source_prediction ?? "Manuel"}</TableCell>
              <TableCell>
                <Badge variant={g.est_virtuelle ? "secondary" : "default"}>
                  {g.est_virtuelle ? "Virtuelle" : "Réelle"}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </>
      }
    />
  );
}
