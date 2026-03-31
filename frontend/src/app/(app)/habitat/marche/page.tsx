"use client";

import { useState } from "react";
import { Building2, MapPinned } from "lucide-react";
import { obtenirMarcheHabitat } from "@/bibliotheque/api/habitat";
import { EntetePageHabitat } from "@/composants/habitat/entete-page-habitat";
import { FiltresMarcheHabitat } from "@/composants/habitat/filtres-marche-habitat";
import { GraphiquesMarcheHabitat } from "@/composants/habitat/graphiques-marche-habitat";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function MarcheHabitatPage() {
  const [commune, setCommune] = useState("Annecy");
  const [codePostal, setCodePostal] = useState("74000");
  const [typeLocal, setTypeLocal] = useState("Maison");

  const { data, refetch, isFetching } = utiliserRequete(
    ["habitat", "marche", commune, codePostal, typeLocal],
    () => obtenirMarcheHabitat({ commune, code_postal: codePostal, type_local: typeLocal, limite: 180 })
  );

  return (
    <div className="space-y-6">
      <EntetePageHabitat
        badge="H12 • Marche local"
        titre="Marche Habitat"
        description="Lecture du marche immobilier local a partir des transactions DVF publiques, avec historique de prix, volumes et reperes exploitables pour la veille Habitat."
        stats={[
          { label: "Transactions", valeur: `${data?.resume.nb_transactions ?? 0}` },
          { label: "Mediane m2", valeur: data?.resume.prix_m2_median ? `${Math.round(data.resume.prix_m2_median).toLocaleString("fr-FR")} EUR` : "-" },
          { label: "Valeur mediane", valeur: data?.resume.valeur_mediane ? `${Math.round(data.resume.valeur_mediane).toLocaleString("fr-FR")} EUR` : "-" },
          { label: "Ressource", valeur: data?.source.resource_title?.split(" - ")[0] ?? "DVF" },
        ]}
      />

      <div className="grid gap-4 xl:grid-cols-[0.92fr_1.08fr]">
        <FiltresMarcheHabitat
          commune={commune}
          codePostal={codePostal}
          typeLocal={typeLocal}
          isFetching={isFetching}
          onCommuneChange={setCommune}
          onCodePostalChange={setCodePostal}
          onTypeLocalChange={setTypeLocal}
          onRefresh={() => {
            void refetch();
          }}
        />

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Lecture rapide</CardTitle>
            <CardDescription>Points de repere directement reutilisables dans la veille et les arbitrages budget.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            <div className="rounded-2xl border p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Dernier mois charge</p>
              <p className="mt-2 text-lg font-semibold">{data?.resume.dernier_mois?.mois ?? "-"}</p>
              <p className="text-sm text-muted-foreground">
                {data?.resume.dernier_mois?.transactions ?? 0} transaction(s) · {data?.resume.dernier_mois?.prix_m2_median ? `${Math.round(data.resume.dernier_mois.prix_m2_median).toLocaleString("fr-FR")} EUR/m2` : "prix indisponible"}
              </p>
            </div>
            <div className="rounded-2xl border p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Surface mediane</p>
              <p className="mt-2 text-lg font-semibold">{data?.resume.surface_mediane ? `${Math.round(data.resume.surface_mediane)} m2` : "-"}</p>
              <p className="text-sm text-muted-foreground">Permet de cadrer rapidement les comparables Habitat.</p>
            </div>
            <div className="rounded-2xl border p-4 md:col-span-2">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="secondary"><MapPinned className="mr-1 h-3.5 w-3.5" /> {data?.query.commune ?? commune}</Badge>
                <Badge variant="secondary">{data?.query.code_postal ?? codePostal}</Badge>
                <Badge variant="secondary"><Building2 className="mr-1 h-3.5 w-3.5" /> {data?.query.type_local ?? typeLocal}</Badge>
              </div>
              <p className="mt-3 text-sm text-muted-foreground">
                Source: {data?.source.resource_title ?? "DVF data.gouv"}. Les indicateurs sont calcules sur les transactions publiques filtrees pour la zone courante.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <GraphiquesMarcheHabitat historique={data?.historique ?? []} repartition={data?.repartition_types ?? []} />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Transactions recentes</CardTitle>
          <CardDescription>Extrait recent des ventes utilisees pour le calcul du marche local.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {(data?.transactions ?? []).slice(0, 8).map((transaction) => (
            <div key={`${transaction.date_mutation}-${transaction.adresse ?? transaction.commune}`} className="rounded-2xl border p-4">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <p className="font-medium">{transaction.adresse ?? transaction.commune ?? "Transaction DVF"}</p>
                  <p className="text-sm text-muted-foreground">
                    {transaction.date_mutation} · {transaction.type_local ?? "Local"} · {transaction.commune ?? "Commune"}
                  </p>
                </div>
                <div className="text-sm sm:text-right">
                  <p className="font-semibold">
                    {transaction.valeur_fonciere ? `${Math.round(transaction.valeur_fonciere).toLocaleString("fr-FR")} EUR` : "Montant indisponible"}
                  </p>
                  <p className="text-muted-foreground">
                    {transaction.prix_m2 ? `${Math.round(transaction.prix_m2).toLocaleString("fr-FR")} EUR/m2` : "-"}
                  </p>
                </div>
              </div>
            </div>
          ))}
          {(data?.transactions ?? []).length === 0 ? <p className="text-sm text-muted-foreground">Aucune transaction disponible pour ces filtres.</p> : null}
        </CardContent>
      </Card>
    </div>
  );
}