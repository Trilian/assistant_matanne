"use client";

import { useMemo } from "react";
import { CalendarRange } from "lucide-react";

import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import type { ProjetMaison } from "@/types/maison";

const COULEURS_BARRES: Record<string, string> = {
  en_cours: "bg-blue-500",
  a_faire: "bg-amber-500",
  planifie: "bg-amber-500",
  planifié: "bg-amber-500",
  termine: "bg-emerald-500",
  terminé: "bg-emerald-500",
  annule: "bg-rose-500",
  annulé: "bg-rose-500",
};

const COL_START_CLASSES = [
  "col-start-1", "col-start-2", "col-start-3", "col-start-4", "col-start-5",
  "col-start-6", "col-start-7", "col-start-8", "col-start-9", "col-start-10",
  "col-start-11", "col-start-12", "col-start-13", "col-start-14", "col-start-15",
  "col-start-16", "col-start-17", "col-start-18", "col-start-19", "col-start-20",
];

const COL_SPAN_CLASSES = [
  "col-span-1", "col-span-2", "col-span-3", "col-span-4", "col-span-5",
  "col-span-6", "col-span-7", "col-span-8", "col-span-9", "col-span-10",
  "col-span-11", "col-span-12", "col-span-13", "col-span-14", "col-span-15",
  "col-span-16", "col-span-17", "col-span-18", "col-span-19", "col-span-20",
];

function normaliserStatut(statut?: string) {
  return (statut ?? "a_faire")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "_")
    .toLowerCase();
}

function lireDate(valeur?: string | null) {
  if (!valeur) {
    return null;
  }
  const date = new Date(valeur);
  return Number.isNaN(date.getTime()) ? null : date;
}

function ajouterJours(date: Date, jours: number) {
  const copie = new Date(date);
  copie.setDate(copie.getDate() + jours);
  return copie;
}

export function GanttProjets({ projets }: { projets: ProjetMaison[] }) {
  const donnees = useMemo(() => {
    if (!projets.length) {
      return [] as Array<{
        projet: ProjetMaison;
        debut: Date;
        fin: Date;
        left: number;
        width: number;
        statutNormalise: string;
      }>;
    }

    const prepares = projets.slice(0, 8).map((projet, index) => {
      const debut = lireDate(projet.date_debut) ?? ajouterJours(new Date(), index * 3);
      const fin =
        lireDate(projet.date_fin_reelle) ??
        lireDate(projet.date_fin_prevue) ??
        ajouterJours(debut, 10 + index * 2);

      return {
        projet,
        debut,
        fin: fin >= debut ? fin : ajouterJours(debut, 4),
        statutNormalise: normaliserStatut(projet.statut),
      };
    });

    const borneMin = Math.min(...prepares.map((item) => item.debut.getTime()));
    const borneMax = Math.max(...prepares.map((item) => item.fin.getTime()));
    const dureeTotale = Math.max(24 * 60 * 60 * 1000, borneMax - borneMin);

    return prepares.map((item) => {
      const left = ((item.debut.getTime() - borneMin) / dureeTotale) * 100;
      const width = Math.max(12, ((item.fin.getTime() - item.debut.getTime()) / dureeTotale) * 100);
      const startIndex = Math.min(20, Math.max(1, Math.round(left / 5) + 1));
      const spanIndex = Math.min(20, Math.max(2, Math.round(width / 5)));
      return {
        ...item,
        left,
        width,
        startIndex,
        spanIndex,
      };
    });
  }, [projets]);

  if (!donnees.length) {
    return null;
  }

  const bornes = donnees.reduce(
    (acc, item) => ({
      min: acc.min < item.debut ? acc.min : item.debut,
      max: acc.max > item.fin ? acc.max : item.fin,
    }),
    { min: donnees[0].debut, max: donnees[0].fin }
  );

  const repereDates = Array.from({ length: 5 }).map((_, index) => {
    const ratio = index / 4;
    const temps = bornes.min.getTime() + (bornes.max.getTime() - bornes.min.getTime()) * ratio;
    return new Date(temps).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
  });

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <CalendarRange className="h-4 w-4 text-primary" />
          Vue Gantt des projets
        </CardTitle>
        <CardDescription>
          Chronologie rapide des travaux en cours, à lancer et à terminer.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-[220px_1fr] gap-3 text-xs text-muted-foreground">
          <div>Projet</div>
          <div className="grid grid-cols-5 gap-2">
            {repereDates.map((repere, index) => (
              <span key={`${repere}-${index}`}>{repere}</span>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          {donnees.map(({ projet, debut, fin, startIndex, spanIndex, statutNormalise }) => (
            <div key={projet.id} className="grid grid-cols-[220px_1fr] items-center gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{projet.nom}</p>
                <div className="mt-1 flex flex-wrap gap-1">
                  <Badge variant="outline">{projet.taches_count} tâche(s)</Badge>
                  {projet.priorite ? <Badge variant="secondary">{projet.priorite}</Badge> : null}
                </div>
              </div>

              <div className="space-y-1">
                <div className="grid h-8 grid-cols-20 gap-1 rounded-full bg-muted/50 p-1">
                  <div
                    className={`${COL_START_CLASSES[startIndex - 1]} ${COL_SPAN_CLASSES[spanIndex - 1]} flex h-6 items-center rounded-full px-3 text-xs font-medium text-white shadow-sm ${
                      COULEURS_BARRES[statutNormalise] ?? "bg-slate-500"
                    }`}
                  >
                    <span className="truncate">{projet.statut.replace(/_/g, " ")}</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  {debut.toLocaleDateString("fr-FR")} → {fin.toLocaleDateString("fr-FR")}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
