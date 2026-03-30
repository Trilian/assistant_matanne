"use client";

import { useState } from "react";
import {
  listerAlertesHabitat,
  listerAnnoncesHabitat,
  obtenirCarteHabitat,
  synchroniserVeilleHabitat,
} from "@/bibliotheque/api/habitat";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Input } from "@/composants/ui/input";
import { utiliserMutationAvecInvalidation, utiliserRequete } from "@/crochets/utiliser-api";

const POSITION_CLASSES = [
  "0", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80", "85", "90", "95",
].map((value) => ({
  left: `left-[${value}%]`,
  top: `top-[${value}%]`,
}));

function positionDepuisCoordonnee(value: number | undefined, min: number, max: number) {
  if (typeof value !== "number" || Number.isNaN(value) || max === min) {
    return 50;
  }
  return ((value - min) / (max - min)) * 100;
}

function classePosition(value: number, axis: "left" | "top") {
  const index = Math.max(0, Math.min(POSITION_CLASSES.length - 1, Math.round(value / 5)));
  return POSITION_CLASSES[index][axis];
}

export default function VeilleImmoHabitatPage() {
  const [limiteParSource, setLimiteParSource] = useState("10");
  const { data: annonces } = utiliserRequete(["habitat", "annonces"], listerAnnoncesHabitat);
  const { data: alertes } = utiliserRequete(["habitat", "alertes"], listerAlertesHabitat);
  const { data: carte } = utiliserRequete(["habitat", "carte"], obtenirCarteHabitat);

  const syncMutation = utiliserMutationAvecInvalidation(
    (payload: { limite_par_source: number }) => synchroniserVeilleHabitat(payload),
    [["habitat", "annonces"], ["habitat", "alertes"], ["habitat", "carte"], ["habitat", "hub"]]
  );

  const latitudes = (carte ?? []).map((point) => point.latitude).filter((value): value is number => typeof value === "number");
  const longitudes = (carte ?? []).map((point) => point.longitude).filter((value): value is number => typeof value === "number");
  const minLat = latitudes.length ? Math.min(...latitudes) : 42;
  const maxLat = latitudes.length ? Math.max(...latitudes) : 51;
  const minLng = longitudes.length ? Math.min(...longitudes) : -5;
  const maxLng = longitudes.length ? Math.max(...longitudes) : 8;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Veille Immo</h1>
          <p className="text-muted-foreground">
            Scraping HTTP réel, scoring des opportunites, carte par ville et alertes prêtes a notifier.
          </p>
        </div>

        <div className="flex gap-2">
          <Input
            value={limiteParSource}
            onChange={(event) => setLimiteParSource(event.target.value)}
            className="w-28"
            inputMode="numeric"
          />
          <Button
            onClick={() => syncMutation.mutate({ limite_par_source: Number(limiteParSource) || 10 })}
            disabled={syncMutation.isPending}
          >
            {syncMutation.isPending ? "Sync..." : "Synchroniser"}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Carte des opportunites</CardTitle>
            <CardDescription>Positionnement par ville via geo.api.gouv.fr.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative h-[420px] overflow-hidden rounded-xl border bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.12),_transparent_35%),linear-gradient(180deg,rgba(248,250,252,1),rgba(226,232,240,0.6))]">
              {(carte ?? []).map((point) => {
                const left = positionDepuisCoordonnee(point.longitude, minLng, maxLng);
                const top = 100 - positionDepuisCoordonnee(point.latitude, minLat, maxLat);
                return (
                  <div
                    key={`${point.ville}-${point.code_postal}`}
                    className={`absolute -translate-x-1/2 -translate-y-1/2 ${classePosition(left, "left")} ${classePosition(top, "top")}`}
                  >
                    <div className="rounded-full border border-white/70 bg-emerald-600/85 px-3 py-1 text-[11px] font-medium text-white shadow-lg">
                      {point.ville} · {point.nb_annonces}
                    </div>
                  </div>
                );
              })}
              {(carte ?? []).length === 0 && (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  Aucune donnee cartographique pour le moment.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Alertes avancees</CardTitle>
            <CardDescription>Score élevé ou prix inférieur au secteur.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
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
            </a>
          ))}
          {(annonces ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucune annonce disponible.</p>}
        </CardContent>
      </Card>
    </div>
  );
}