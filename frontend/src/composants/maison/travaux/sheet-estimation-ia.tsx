"use client";

import { BotMessageSquare, AlertTriangle, CheckCircle2 } from "lucide-react";

import { Skeleton } from "@/composants/ui/skeleton";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/composants/ui/sheet";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { estimerProjetIA } from "@/bibliotheque/api/maison";
import { BoutonAchat } from "@/composants/bouton-achat";

export function SheetEstimationIA({
  projetId,
  ouvert,
  onFermer,
}: {
  projetId: number | null;
  ouvert: boolean;
  onFermer: () => void;
}) {
  const { data: estimation, isLoading, error } = utiliserRequete(
    ["maison", "projets", String(projetId ?? ""), "estimation-ia"],
    () => estimerProjetIA(projetId!),
    { enabled: ouvert && projetId !== null, staleTime: 30 * 60 * 1000 }
  );

  return (
    <Sheet open={ouvert} onOpenChange={(o) => !o && onFermer()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <BotMessageSquare className="h-5 w-5 text-primary" />
            Estimation IA
          </SheetTitle>
        </SheetHeader>

        {isLoading && (
          <div className="mt-6 space-y-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-24" />
            <Skeleton className="h-32" />
          </div>
        )}

        {error && (
          <div className="mt-6 text-sm text-destructive">
            Impossible de générer l&apos;estimation. Vérifiez que le projet a une description.
          </div>
        )}

        {estimation && (
          <div className="mt-6 space-y-6">
            <div className="space-y-1 rounded-lg border bg-muted/30 p-4">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Budget estimé</p>
              <p className="text-2xl font-bold">
                {estimation.budget_estime_min.toLocaleString("fr-FR")} €
                {" – "}
                {estimation.budget_estime_max.toLocaleString("fr-FR")} €
              </p>
              <p className="text-xs text-muted-foreground">
                Durée estimée : {estimation.duree_estimee_jours} jour{estimation.duree_estimee_jours > 1 ? "s" : ""}
              </p>
            </div>

            {estimation.taches_suggerees.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Étapes suggérées</p>
                <ol className="space-y-2">
                  {estimation.taches_suggerees.map((t, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <span className="shrink-0 font-bold text-primary">{i + 1}.</span>
                      <span className="flex-1">
                        {t.nom}
                        {t.duree_estimee_min && (
                          <span className="ml-1 text-xs text-muted-foreground">({t.duree_estimee_min} min)</span>
                        )}
                      </span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {estimation.materiels_necessaires.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Matériaux nécessaires</p>
                <div className="space-y-2">
                  {estimation.materiels_necessaires.map((m, i) => (
                    <div key={i} className="flex items-center justify-between gap-2 rounded-md border p-2 text-sm">
                      <div className="min-w-0">
                        <p className="truncate font-medium">{m.nom} × {m.quantite}</p>
                        {m.magasin_suggere && <p className="text-xs text-muted-foreground">{m.magasin_suggere}</p>}
                        {m.alternatif_eco && <p className="text-xs text-green-600">💡 {m.alternatif_eco}</p>}
                      </div>
                      <div className="flex shrink-0 items-center gap-2">
                        {m.prix_estime && <span className="text-xs font-semibold">{m.prix_estime} €</span>}
                        <BoutonAchat article={{ nom: m.nom }} taille="xs" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {estimation.risques_identifies.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Points de vigilance</p>
                <ul className="space-y-1">
                  {estimation.risques_identifies.map((risque, i) => (
                    <li key={i} className="flex gap-2 text-sm text-amber-700">
                      <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      {risque}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {estimation.conseils_ia.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Conseils</p>
                <ul className="space-y-1">
                  {estimation.conseils_ia.map((conseil, i) => (
                    <li key={i} className="flex gap-2 text-sm">
                      <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-green-600" />
                      {conseil}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
