"use client";

import { useState } from "react";
import { Building2, MapPinned, BarChart3, Map } from "lucide-react";
import { obtenirBarometreHabitat, obtenirMarcheHabitat } from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { FiltresMarcheHabitat } from "@/composants/habitat/filtres-marche-habitat";
import { GraphiquesMarcheHabitat } from "@/composants/habitat/graphiques-marche-habitat";
import { GraphiquesBarometre } from "@/composants/habitat/graphiques-barometre";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function MarcheHabitatPage() {
  const [commune, setCommune] = useState("Annecy");
  const [codePostal, setCodePostal] = useState("74000");
  const [typeLocal, setTypeLocal] = useState("Maison");
  const [nbPiecesMin, setNbPiecesMin] = useState("");

  // ─── Analyse locale (DVF commune) ─────────────────────────────────
  const { data, refetch, isFetching } = utiliserRequete(
    ["habitat", "marche", commune, codePostal, typeLocal, nbPiecesMin],
    () =>
      obtenirMarcheHabitat({
        commune,
        code_postal: codePostal,
        type_local: typeLocal || undefined,
        nb_pieces_min: nbPiecesMin ? parseInt(nbPiecesMin) : undefined,
        limite: 180,
      })
  );

  // ─── Baromètre national ────────────────────────────────────────────
  const {
    data: barometre,
    refetch: refetchBarometre,
    isFetching: isFetchingBarometre,
  } = utiliserRequete(
    ["habitat", "barometre", typeLocal],
    () =>
      obtenirBarometreHabitat({
        type_local: typeLocal || undefined,
        ma_commune: commune,
        mon_code_postal: codePostal,
        limite_par_ville: 80,
      }),
    { staleTime: 1000 * 60 * 15 } // cache 15 min (appel lent)
  );

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H12 • Marché immobilier"
        titre="Marché"
        description="Analyse du marché local et baromètre national basés sur les transactions DVF publiques (data.gouv.fr)."
        stats={[
          { label: "Transactions locales", valeur: `${data?.resume.nb_transactions ?? 0}` },
          {
            label: "Médiane/m² locale",
            valeur: data?.resume.prix_m2_median
              ? `${Math.round(data.resume.prix_m2_median).toLocaleString("fr-FR")} €`
              : "—",
          },
          {
            label: "Villes comparées",
            valeur: `${barometre?.villes.length ?? "…"}`,
          },
          {
            label: "Rang local",
            valeur: barometre?.rang_local != null
              ? `${barometre.rang_local}/${barometre.villes.length}`
              : "—",
          },
        ]}
      />

      <Tabs defaultValue="local">
        <TabsList>
          <TabsTrigger value="local" className="gap-2">
            <Map className="h-4 w-4" />
            Analyse locale
          </TabsTrigger>
          <TabsTrigger value="barometre" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            Baromètre national
          </TabsTrigger>
        </TabsList>

        {/* ── ONGLET 1 : Analyse locale ─────────────────────────────── */}
        <TabsContent value="local" className="space-y-6 pt-4">
          <div className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
            <FiltresMarcheHabitat
              commune={commune}
              codePostal={codePostal}
              typeLocal={typeLocal}
              nbPiecesMin={nbPiecesMin}
              isFetching={isFetching}
              onCommuneChange={setCommune}
              onCodePostalChange={setCodePostal}
              onTypeLocalChange={setTypeLocal}
              onNbPiecesMinChange={setNbPiecesMin}
              onRefresh={() => { void refetch(); }}
            />

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Lecture rapide</CardTitle>
                <CardDescription>
                  Points de repère directement réutilisables dans la veille et les arbitrages budget.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-2">
                <div className="rounded-2xl border p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Dernier mois chargé</p>
                  <p className="mt-2 text-lg font-semibold">{data?.resume.dernier_mois?.mois ?? "—"}</p>
                  <p className="text-sm text-muted-foreground">
                    {data?.resume.dernier_mois?.transactions ?? 0} transaction(s) ·{" "}
                    {data?.resume.dernier_mois?.prix_m2_median
                      ? `${Math.round(data.resume.dernier_mois.prix_m2_median).toLocaleString("fr-FR")} €/m²`
                      : "prix indisponible"}
                  </p>
                </div>
                <div className="rounded-2xl border p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Surface médiane</p>
                  <p className="mt-2 text-lg font-semibold">
                    {data?.resume.surface_mediane ? `${Math.round(data.resume.surface_mediane)} m²` : "—"}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Permet de cadrer rapidement les comparables Habitat.
                  </p>
                </div>
                <div className="rounded-2xl border p-4 md:col-span-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="secondary">
                      <MapPinned className="mr-1 h-3.5 w-3.5" />
                      {data?.query.commune ?? commune}
                    </Badge>
                    <Badge variant="secondary">{data?.query.code_postal ?? codePostal}</Badge>
                    <Badge variant="secondary">
                      <Building2 className="mr-1 h-3.5 w-3.5" />
                      {data?.query.type_local || "Toutes typologies"}
                    </Badge>
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">
                    Source : {data?.source.resource_title ?? "DVF data.gouv"}. Indicateurs calculés
                    sur les transactions publiques filtrées pour la zone courante.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          <GraphiquesMarcheHabitat
            historique={data?.historique ?? []}
            repartition={data?.repartition_types ?? []}
          />

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Transactions récentes</CardTitle>
              <CardDescription>
                Extrait des ventes utilisées pour le calcul du marché local.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {(data?.transactions ?? []).slice(0, 8).map((transaction) => (
                <div
                  key={`${transaction.date_mutation}-${transaction.adresse ?? transaction.commune}`}
                  className="rounded-2xl border p-4"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="font-medium">
                        {transaction.adresse ?? transaction.commune ?? "Transaction DVF"}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {transaction.date_mutation} · {transaction.type_local ?? "Local"} ·{" "}
                        {transaction.commune ?? "Commune"}
                      </p>
                    </div>
                    <div className="text-sm sm:text-right">
                      <p className="font-semibold">
                        {transaction.valeur_fonciere
                          ? `${Math.round(transaction.valeur_fonciere).toLocaleString("fr-FR")} €`
                          : "Montant indisponible"}
                      </p>
                      <p className="text-muted-foreground">
                        {transaction.prix_m2
                          ? `${Math.round(transaction.prix_m2).toLocaleString("fr-FR")} €/m²`
                          : "—"}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {(data?.transactions ?? []).length === 0 && (
                <p className="text-sm text-muted-foreground">
                  Aucune transaction disponible pour ces filtres.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── ONGLET 2 : Baromètre national ─────────────────────────── */}
        <TabsContent value="barometre" className="space-y-6 pt-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm text-muted-foreground">
                Comparaison du prix médian au m² entre {barometre?.villes.length ?? "…"} villes de référence
                {commune ? ` · votre zone : ${commune}` : ""}.
                {barometre?.updated_at
                  ? ` Mis à jour : ${new Date(barometre.updated_at).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}.`
                  : ""}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              disabled={isFetchingBarometre}
              onClick={() => { void refetchBarometre(); }}
            >
              {isFetchingBarometre ? "Chargement…" : "Actualiser le baromètre"}
            </Button>
          </div>

          {isFetchingBarometre && (
            <Card className="p-8 text-center text-muted-foreground">
              <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="text-sm">
                Chargement en cours — interrogation de {10} villes de référence via DVF…
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Cette opération peut prendre 15 à 30 secondes.
              </p>
            </Card>
          )}

          {!isFetchingBarometre && barometre && (
            <GraphiquesBarometre barometre={barometre} />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
