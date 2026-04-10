"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import { BellRing, MapPinned, RadioTower } from "lucide-react";
import {
  listerAlertesHabitat,
  listerAnnoncesHabitat,
  obtenirCarteHabitat,
  synchroniserVeilleHabitat,
} from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";
import { evaluerFraicheurSync, libelleFraicheurSync } from "@/bibliotheque/habitat-fraicheur-sync";

const CarteVeilleHabitat = dynamic(
  () => import("@/composants/habitat/carte-veille-habitat").then((mod) => mod.CarteVeilleHabitat),
  { ssr: false, loading: () => <div className="h-[420px] animate-pulse rounded-2xl border bg-muted/40" /> }
);

const SOURCES_DISPONIBLES = ["leboncoin", "bienici", "seloger", "pap"];

interface DerniereSyncVeille {
  dateIso: string;
  limiteParSource: number;
  sources: string[];
  annoncesCreees: number;
  annoncesMisesAJour: number;
  alertes: number;
}


export default function VeilleImmoHabitatPage() {
  const [limiteParSource, setLimiteParSource] = useState("10");
  const [sourcesSelectionnees, setSourcesSelectionnees] = utiliserStockageLocal<string[]>(
    "habitat.veille.sources",
    SOURCES_DISPONIBLES
  );
  const [derniereSync, setDerniereSync, reinitialiserDerniereSync] = utiliserStockageLocal<DerniereSyncVeille | null>(
    "habitat.veille.derniere-sync",
    null
  );
  const { data: annonces } = utiliserRequete(["habitat", "annonces"], listerAnnoncesHabitat);
  const { data: alertes } = utiliserRequete(["habitat", "alertes"], listerAlertesHabitat);
  const { data: carte } = utiliserRequete(["habitat", "carte"], obtenirCarteHabitat);

  const syncMutation = utiliserMutationAvecInvalidation(
    (payload: { limite_par_source: number; sources: string[] }) => synchroniserVeilleHabitat(payload),
    [["habitat", "annonces"], ["habitat", "alertes"], ["habitat", "carte"], ["habitat", "hub"]]
  );

  function basculerSource(source: string) {
    setSourcesSelectionnees((courant) => {
      const existe = courant.includes(source);
      if (existe) {
        const suivant = courant.filter((item) => item !== source);
        return suivant.length > 0 ? suivant : [source];
      }
      return [...courant, source];
    });
  }

  async function lancerSynchronisation() {
    const limite = Number(limiteParSource) || 10;
    const resultat = await syncMutation.mutateAsync({
      limite_par_source: limite,
      sources: sourcesSelectionnees,
    });
    setDerniereSync({
      dateIso: new Date().toISOString(),
      limiteParSource: limite,
      sources: sourcesSelectionnees,
      annoncesCreees: resultat.annonces_creees,
      annoncesMisesAJour: resultat.annonces_mises_a_jour,
      alertes: resultat.alertes,
    });
  }

  const statsSources = syncMutation.data?.stats_sources ?? [];
  const etatFraicheur = derniereSync ? evaluerFraicheurSync(derniereSync.dateIso) : null;
  const annoncesParSource = (annonces ?? []).reduce<Record<string, number>>((acc, annonce) => {
    acc[annonce.source] = (acc[annonce.source] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H3-H4 • Veille renforcee"
        titre="Veille Immo"
        description="Connecteurs par source, scoring des opportunites, carte geographique reelle et alertes directement actionnables avant visite ou arbitrage." 
        stats={[
          { label: "Annonces", valeur: `${annonces?.length ?? 0}` },
          { label: "Alertes", valeur: `${alertes?.length ?? 0}` },
          { label: "Points carte", valeur: `${carte?.length ?? 0}` },
          { label: "Sources", valeur: `${Object.keys(annoncesParSource).length}` },
        ]}
        actions={(
          <div className="flex gap-2">
          <Input
            value={limiteParSource}
            onChange={(event) => setLimiteParSource(event.target.value)}
            className="w-28"
            inputMode="numeric"
          />
          <Button
            onClick={() => {
              void lancerSynchronisation();
            }}
            disabled={syncMutation.isPending}
          >
            {syncMutation.isPending ? "Sync..." : "Synchroniser"}
          </Button>
          </div>
        )}
      />

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Carte des opportunites</CardTitle>
            <CardDescription>Leaflet + OpenStreetMap, avec agrégation par ville et score de priorite.</CardDescription>
          </CardHeader>
          <CardContent>
            {(carte ?? []).length > 0 ? <CarteVeilleHabitat points={carte ?? []} /> : <div className="flex h-[420px] items-center justify-center rounded-2xl border text-sm text-muted-foreground">Aucune donnee cartographique pour le moment.</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Alertes avancees</CardTitle>
            <CardDescription>Score élevé ou prix inférieur au secteur.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
              <div className="rounded-2xl border p-3 text-sm">
                <p className="flex items-center gap-2 font-medium"><BellRing className="h-4 w-4" /> Alertes fortes</p>
                <p className="mt-2 text-2xl font-semibold">{(alertes ?? []).filter((item) => (item.score ?? 0) >= 0.8).length}</p>
              </div>
              <div className="rounded-2xl border p-3 text-sm">
                <p className="flex items-center gap-2 font-medium"><MapPinned className="h-4 w-4" /> Villes suivies</p>
                <p className="mt-2 text-2xl font-semibold">{carte?.length ?? 0}</p>
              </div>
              <div className="rounded-2xl border p-3 text-sm">
                <p className="flex items-center gap-2 font-medium"><RadioTower className="h-4 w-4" /> Sources actives</p>
                <p className="mt-2 text-2xl font-semibold">{Object.keys(annoncesParSource).length}</p>
              </div>
            </div>
            {(alertes ?? []).map((alerte) => (
              <a
                key={`${alerte.url_source}-${alerte.titre}`}
                href={alerte.url_source}
                target="_blank"
                rel="noreferrer"
                className="block rounded-xl border p-3 transition-colors hover:bg-accent/40"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{alerte.titre ?? "Annonce sans titre"}</p>
                    <p className="text-xs text-muted-foreground">
                      {alerte.source} · {alerte.ville ?? "Ville inconnue"} · {alerte.prix ?? "?"} EUR
                    </p>
                  </div>
                  <div className="flex flex-col gap-2 text-right">
                    <Badge variant="secondary">score {(alerte.score ?? 0).toFixed(2)}</Badge>
                    {typeof alerte.ecart_prix_pct === "number" && (
                      <Badge variant={alerte.ecart_prix_pct <= -10 ? "default" : "outline"}>
                        {alerte.ecart_prix_pct.toFixed(1)}%
                      </Badge>
                    )}
                  </div>
                </div>
              </a>
            ))}
            {(alertes ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucune alerte active.</p>}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Derniere sync</CardTitle>
          <CardDescription>Memo locale de la derniere execution pour garder un contexte rapide entre deux sessions.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {derniereSync ? (
            <>
              <div className="flex flex-wrap items-center gap-2">
                {etatFraicheur === "stale" ? (
                  <Badge className="border-red-300 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200" variant="outline">
                    {libelleFraicheurSync("stale")}
                  </Badge>
                ) : null}
                {etatFraicheur === "warning" ? (
                  <Badge className="border-amber-300 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200" variant="outline">
                    {libelleFraicheurSync("warning")}
                  </Badge>
                ) : null}
                {etatFraicheur === "fresh" ? <Badge variant="secondary">{libelleFraicheurSync("fresh")}</Badge> : null}
                <Button variant="ghost" size="sm" onClick={reinitialiserDerniereSync}>
                  Effacer l'historique local
                </Button>
              </div>

              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
              <div className="rounded-2xl border p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Date</p>
                <p className="mt-1 text-sm font-medium">{new Date(derniereSync.dateIso).toLocaleString("fr-FR")}</p>
              </div>
              <div className="rounded-2xl border p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Limite/source</p>
                <p className="mt-1 text-sm font-medium">{derniereSync.limiteParSource}</p>
              </div>
              <div className="rounded-2xl border p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Creees</p>
                <p className="mt-1 text-sm font-medium">{derniereSync.annoncesCreees}</p>
              </div>
              <div className="rounded-2xl border p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Mises a jour</p>
                <p className="mt-1 text-sm font-medium">{derniereSync.annoncesMisesAJour}</p>
              </div>
              <div className="rounded-2xl border p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Alertes</p>
                <p className="mt-1 text-sm font-medium">{derniereSync.alertes}</p>
              </div>
              <div className="md:col-span-2 xl:col-span-5 rounded-2xl border p-3">
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Sources executees</p>
                <p className="mt-1 text-sm font-medium">{derniereSync.sources.join(", ")}</p>
              </div>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Aucune synchronisation mémorisée pour le moment.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Couverture par source</CardTitle>
          <CardDescription>Retour du dernier cycle de synchronisation et poids actuel par portail. Les sources actives sont mémorisées localement.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {SOURCES_DISPONIBLES.map((source) => {
              const active = sourcesSelectionnees.includes(source);
              return (
                <Button
                  key={source}
                  variant={active ? "default" : "outline"}
                  size="sm"
                  onClick={() => basculerSource(source)}
                  className="capitalize"
                >
                  {source}
                </Button>
              );
            })}
          </div>

          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {(statsSources.length > 0 ? statsSources : Object.entries(annoncesParSource).map(([source, count]) => ({ source, url: "", annonces: count, alertes: 0 }))).map((stat) => (
            <div key={stat.source} className="rounded-2xl border p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-medium capitalize">{stat.source}</p>
                <Badge variant="secondary">{stat.annonces} annonces</Badge>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{stat.alertes} alerte(s) detectee(s)</p>
              {stat.url ? <p className="mt-2 line-clamp-2 text-xs text-muted-foreground">{stat.url}</p> : null}
            </div>
          ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Annonces synchronisees</CardTitle>
          <CardDescription>Vue consolidée des annonces scrappées ou importées.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {(annonces ?? []).map((annonce) => (
            <a
              key={annonce.id}
              href={annonce.url_source}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl border p-4 transition-colors hover:bg-accent/40"
            >
              <div className="mb-2 flex items-start justify-between gap-3">
                <p className="font-medium">{annonce.titre ?? "Annonce sans titre"}</p>
                <Badge variant={annonce.statut === "alerte" ? "default" : "outline"}>{annonce.statut}</Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                {annonce.source} · {annonce.ville ?? "Ville inconnue"} · {annonce.prix ?? "?"} EUR
              </p>
              <p className="mt-2 text-xs text-muted-foreground">
                {annonce.surface_m2 ?? "?"} m2 · {annonce.nb_pieces ?? "?"} pieces · score {(annonce.score_pertinence ?? 0).toFixed(2)}
              </p>
              {typeof annonce.ecart_prix_pct === "number" ? <p className="mt-2 text-xs text-muted-foreground">Ecart secteur: {annonce.ecart_prix_pct.toFixed(1)}%</p> : null}
            </a>
          ))}
          {(annonces ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucune annonce disponible.</p>}
        </CardContent>
      </Card>
    </div>
  );
}