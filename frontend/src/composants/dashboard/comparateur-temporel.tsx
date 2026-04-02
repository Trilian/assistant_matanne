"use client";

import { useMemo, useState } from "react";
import { ArrowLeftRight, CalendarRange } from "lucide-react";

import { obtenirBilanMensuel } from "@/bibliotheque/api/tableau-bord";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Slider } from "@/composants/ui/slider";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";

function moisOffset(offset: number) {
  const date = new Date();
  date.setMonth(date.getMonth() - offset);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function libelleMois(mois: string) {
  const [annee, numero] = mois.split("-").map(Number);
  return new Date(annee, (numero || 1) - 1, 1).toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });
}

function classeLargeur(valeur: number) {
  const pourcentage = Math.max(0, Math.min(100, Math.round(valeur / 10) * 10));
  const classes: Record<number, string> = {
    0: "w-0",
    10: "w-[10%]",
    20: "w-[20%]",
    30: "w-[30%]",
    40: "w-[40%]",
    50: "w-[50%]",
    60: "w-[60%]",
    70: "w-[70%]",
    80: "w-[80%]",
    90: "w-[90%]",
    100: "w-full",
  };
  return classes[pourcentage] ?? "w-0";
}

export function ComparateurTemporel() {
  const moisDisponibles = useMemo(
    () => Array.from({ length: 6 }, (_, index) => moisOffset(5 - index)),
    []
  );
  const [indexActif, setIndexActif] = useState([5]);
  const moisActif = moisDisponibles[indexActif[0]];
  const moisPrecedent = moisDisponibles[Math.max(0, indexActif[0] - 1)];

  const { data: courant, isLoading: chargementCourant } = utiliserRequete(
    ["dashboard", "bilan-mensuel", moisActif],
    () => obtenirBilanMensuel(moisActif)
  );
  const { data: precedent, isLoading: chargementPrecedent } = utiliserRequete(
    ["dashboard", "bilan-mensuel", moisPrecedent],
    () => obtenirBilanMensuel(moisPrecedent),
    { enabled: Boolean(moisPrecedent) }
  );

  const cartes = [
    {
      cle: "depenses",
      titre: "Dépenses",
      courant: courant?.donnees.depenses.total ?? 0,
      precedent: precedent?.donnees.depenses.total ?? 0,
      unite: "€",
    },
    {
      cle: "repas",
      titre: "Repas planifiés",
      courant: courant?.donnees.repas.total_planifies ?? 0,
      precedent: precedent?.donnees.repas.total_planifies ?? 0,
      unite: "repas",
    },
    {
      cle: "activites",
      titre: "Activités",
      courant: courant?.donnees.activites.total ?? 0,
      precedent: precedent?.donnees.activites.total ?? 0,
      unite: "act.",
    },
  ];

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <ArrowLeftRight className="h-4 w-4" />
          Comparateur temporel
        </CardTitle>
        <CardDescription>
          Faites glisser le curseur pour comparer les métriques mois par mois.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-xl border bg-muted/30 p-4">
          <div className="mb-3 flex items-center justify-between gap-3 text-sm">
            <span className="flex items-center gap-2 font-medium">
              <CalendarRange className="h-4 w-4" />
              {libelleMois(moisActif)}
            </span>
            <span className="text-muted-foreground">
              {moisPrecedent ? `vs ${libelleMois(moisPrecedent)}` : "Premier point disponible"}
            </span>
          </div>
          <Slider value={indexActif} min={0} max={moisDisponibles.length - 1} step={1} onValueChange={setIndexActif} />
        </div>

        {chargementCourant || chargementPrecedent ? (
          <div className="grid gap-3 md:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-28" />
            ))}
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-3">
            {cartes.map((carte) => {
              const max = Math.max(carte.courant, carte.precedent, 1);
              const delta = carte.courant - carte.precedent;
              return (
                <div key={carte.cle} className="rounded-2xl border p-4">
                  <p className="text-sm text-muted-foreground">{carte.titre}</p>
                  <p className="mt-1 text-2xl font-semibold">
                    {carte.courant.toFixed(0)} {carte.unite}
                  </p>
                  <p className={`mt-1 text-xs ${delta > 0 ? "text-orange-600" : delta < 0 ? "text-emerald-600" : "text-muted-foreground"}`}>
                    {delta > 0 ? "+" : ""}
                    {delta.toFixed(0)} {carte.unite}
                  </p>
                  <div className="mt-3 space-y-2">
                    <div>
                      <div className="mb-1 flex justify-between text-[11px] text-muted-foreground">
                        <span>{libelleMois(moisActif)}</span>
                        <span>{carte.courant.toFixed(0)}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted">
                        <div className={`h-full rounded-full bg-primary ${classeLargeur((carte.courant / max) * 100)}`} />
                      </div>
                    </div>
                    <div>
                      <div className="mb-1 flex justify-between text-[11px] text-muted-foreground">
                        <span>{moisPrecedent ? libelleMois(moisPrecedent) : "-"}</span>
                        <span>{carte.precedent.toFixed(0)}</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted">
                        <div className={`h-full rounded-full bg-slate-400 ${classeLargeur((carte.precedent / max) * 100)}`} />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
