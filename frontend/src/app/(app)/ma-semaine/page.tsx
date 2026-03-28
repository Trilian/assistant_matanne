// ═══════════════════════════════════════════════════════════
// Ma Semaine — Vue trans-modules unifiée (AC1)
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import {
  UtensilsCrossed,
  Baby,
  SprayCan,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirSemaineUnifiee } from "@/bibliotheque/api/planning";
import { useState } from "react";

const JOURS_COURT = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
const TYPE_REPAS_LABEL: Record<string, string> = {
  dejeuner: "Déjeuner",
  diner: "Dîner",
  petit_dejeuner: "Matin",
};

function lundi(offset = 0): string {
  const d = new Date();
  d.setDate(d.getDate() - d.getDay() + 1 + offset * 7);
  return d.toISOString().split("T")[0];
}

function formatDateCourtFr(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("fr-FR", { weekday: "short", day: "numeric", month: "short" });
}

export default function PageMaSemaine() {
  const [offsetSemaine, setOffsetSemaine] = useState(0);
  const dateDebut = lundi(offsetSemaine);

  const { data, isLoading, isError } = utiliserRequete(
    ["planning", "semaine-unifiee", dateDebut],
    () => obtenirSemaineUnifiee(dateDebut),
    { staleTime: 5 * 60 * 1000 }
  );

  // Générer les 7 jours de la semaine
  const jours: string[] = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(dateDebut + "T00:00:00");
    d.setDate(d.getDate() + i);
    return d.toISOString().split("T")[0];
  });

  const titresSemaine = data
    ? `${formatDateCourtFr(data.meta.semaine_debut)} – ${formatDateCourtFr(data.meta.semaine_fin)}`
    : "Chargement…";

  return (
    <div className="space-y-6">
      {/* En-tête + navigation semaine */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📅 Ma Semaine</h1>
          <p className="text-sm text-muted-foreground">{titresSemaine}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setOffsetSemaine((o) => o - 1)}
            aria-label="Semaine précédente"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          {offsetSemaine !== 0 && (
            <Button variant="outline" size="sm" onClick={() => setOffsetSemaine(0)}>
              Cette semaine
            </Button>
          )}
          <Button
            variant="outline"
            size="icon"
            onClick={() => setOffsetSemaine((o) => o + 1)}
            aria-label="Semaine suivante"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* État d'erreur */}
      {isError && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Impossible de charger la semaine. Vérifie ta connexion ou réessaie.
        </div>
      )}

      {/* Grille jours × colonnes */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {jours.map((jour, idx) => {
            const repasJour = data?.repas[jour] ?? [];
            const activitesJour = (data?.activites_famille ?? []).filter(
              (a) => a.date === jour
            );

            const isEmpty = !repasJour.length && !activitesJour.length;

            return (
              <Card key={jour} className={isEmpty ? "opacity-50" : ""}>
                <CardHeader className="pb-2 pt-3 px-4">
                  <CardTitle className="text-sm font-semibold text-muted-foreground">
                    {JOURS_COURT[idx]}{" "}
                    <span className="text-foreground">{new Date(jour + "T00:00:00").getDate()}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-4 pb-3 space-y-2">
                  {isEmpty && (
                    <p className="text-xs text-muted-foreground">Rien de prévu</p>
                  )}

                  {/* Repas */}
                  {repasJour.map((r) => (
                    <div key={r.id} className="flex items-center gap-2">
                      <UtensilsCrossed className="h-3.5 w-3.5 text-orange-500 shrink-0" />
                      <span className="text-xs text-muted-foreground w-14 shrink-0">
                        {TYPE_REPAS_LABEL[r.type] ?? r.type}
                      </span>
                      <span className="text-sm truncate">{r.nom_recette ?? "Repas planifié"}</span>
                      <Link href="/cuisine/planning" className="ml-auto">
                        <Badge variant="outline" className="text-xs">→</Badge>
                      </Link>
                    </div>
                  ))}

                  {/* Activités famille */}
                  {activitesJour.map((a) => (
                    <div key={a.id} className="flex items-center gap-2">
                      <Baby className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                      <span className="text-xs text-muted-foreground w-14 shrink-0">
                        {a.type ?? "Activité"}
                      </span>
                      <span className="text-sm truncate">{a.titre}</span>
                      <Link href="/famille/activites" className="ml-auto">
                        <Badge variant="outline" className="text-xs">→</Badge>
                      </Link>
                    </div>
                  ))}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Tâches maison du jour */}
      {!isLoading && (data?.taches_maison ?? []).length > 0 && (
        <section className="space-y-2">
          <h2 className="text-base font-semibold flex items-center gap-2">
            <SprayCan className="h-4 w-4 text-green-600" />
            Tâches maison aujourd'hui
          </h2>
          <Card>
            <CardContent className="pt-4 pb-3 space-y-2">
              {data!.taches_maison.map((t, idx) => (
                <div key={idx} className="flex items-center gap-3 text-sm">
                  <Badge variant="outline" className="text-xs">
                    {t.categorie ?? "Ménage"}
                  </Badge>
                  <span>{t.nom}</span>
                  {t.duree_estimee_min && (
                    <span className="ml-auto text-xs text-muted-foreground">
                      ~{t.duree_estimee_min} min
                    </span>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
          <div className="flex justify-end">
            <Link href="/maison/menage">
              <Button variant="ghost" size="sm" className="text-xs">
                Voir tout le ménage →
              </Button>
            </Link>
          </div>
        </section>
      )}

      {/* Liens rapides */}
      <div className="grid grid-cols-2 gap-3 pt-2">
        <Link href="/cuisine/planning">
          <Card className="hover:bg-accent/50 transition-colors">
            <CardContent className="pt-4 pb-3 text-center">
              <UtensilsCrossed className="h-6 w-6 mx-auto text-orange-500 mb-1" />
              <p className="text-xs font-medium">Gérer les repas</p>
            </CardContent>
          </Card>
        </Link>
        <Link href="/famille/activites">
          <Card className="hover:bg-accent/50 transition-colors">
            <CardContent className="pt-4 pb-3 text-center">
              <Baby className="h-6 w-6 mx-auto text-blue-500 mb-1" />
              <p className="text-xs font-medium">Activités famille</p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
