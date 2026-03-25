// ═══════════════════════════════════════════════════════════
// DrawerProjet — Fiche projet maison avec progression
// ═══════════════════════════════════════════════════════════

"use client";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/composants/ui/sheet";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Progress } from "@/composants/ui/progress";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirProjet, listerTachesProjet } from "@/bibliotheque/api/maison";

interface DrawerProjetProps {
  projetId: number | null;
  ouvert: boolean;
  onFermer: () => void;
}

const STATUT_CONFIG: Record<string, { couleur: string; label: string }> = {
  planifie: { couleur: "bg-blue-100 text-blue-800", label: "Planifié" },
  en_cours: { couleur: "bg-yellow-100 text-yellow-800", label: "En cours" },
  termine: { couleur: "bg-green-100 text-green-800", label: "Terminé" },
  suspendu: { couleur: "bg-gray-100 text-gray-800", label: "Suspendu" },
};

const PRIORITE_CONFIG: Record<string, string> = {
  haute: "text-red-600",
  moyenne: "text-orange-600",
  basse: "text-muted-foreground",
};

function formaterDate(dateStr?: string): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function DrawerProjet({ projetId, ouvert, onFermer }: DrawerProjetProps) {
  const { data: projet, isLoading } = utiliserRequete(
    ["projet-detail", String(projetId)],
    () => obtenirProjet(projetId!),
    { enabled: !!projetId }
  );

  const { data: taches } = utiliserRequete(
    ["projet-taches", String(projetId)],
    () => listerTachesProjet(projetId!),
    { enabled: !!projetId }
  );

  const tachesTerminees = taches?.filter((t) => t.statut === "fait" || t.fait).length ?? 0;
  const totalTaches = taches?.length ?? projet?.taches_count ?? 0;
  const progression = totalTaches > 0 ? Math.round((tachesTerminees / totalTaches) * 100) : 0;

  const statut = projet ? (STATUT_CONFIG[projet.statut] ?? { couleur: "bg-muted", label: projet.statut }) : null;

  return (
    <Sheet open={ouvert} onOpenChange={(o) => !o && onFermer()}>
      <SheetContent side="right" className="w-full sm:w-[460px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{projet?.nom ?? "Projet"}</SheetTitle>
          <SheetDescription>Détails et progression</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-5">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          )}

          {projet && !isLoading && (
            <>
              {/* Statut + Priorité */}
              <div className="flex items-center gap-2 flex-wrap">
                {statut && (
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statut.couleur}`}>
                    {statut.label}
                  </span>
                )}
                {projet.priorite && (
                  <span className={`text-sm font-medium ${PRIORITE_CONFIG[projet.priorite] ?? ""}`}>
                    ↑ {projet.priorite}
                  </span>
                )}
              </div>

              {/* Progression */}
              {totalTaches > 0 && (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progression</span>
                    <span className="font-medium">{tachesTerminees}/{totalTaches} tâches</span>
                  </div>
                  <Progress value={progression} className="h-2" />
                  <p className="text-xs text-muted-foreground">{progression}% complété</p>
                </div>
              )}

              {/* Description */}
              {projet.description && (
                <div className="rounded-lg bg-muted/50 p-3">
                  <p className="text-sm">{projet.description}</p>
                </div>
              )}

              {/* Dates */}
              <div className="rounded-lg border p-4 text-sm space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  <span className="text-muted-foreground">Début</span>
                  <span>{formaterDate(projet.date_debut)}</span>

                  <span className="text-muted-foreground">Fin prévue</span>
                  <span>{formaterDate(projet.date_fin_prevue)}</span>

                  {projet.date_fin_reelle && (
                    <>
                      <span className="text-muted-foreground">Fin réelle</span>
                      <span className="text-green-600">{formaterDate(projet.date_fin_reelle)}</span>
                    </>
                  )}
                </div>
              </div>

              {/* Tâches */}
              {taches && taches.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">Tâches</p>
                  <div className="space-y-1.5 max-h-56 overflow-y-auto">
                    {taches.map((t) => (
                      <div key={t.id} className="flex items-center gap-2 text-sm py-1">
                        <span className={t.fait || t.statut === "fait" ? "text-green-500" : "text-muted-foreground"}>
                          {t.fait || t.statut === "fait" ? "✓" : "○"}
                        </span>
                        <span className={t.fait || t.statut === "fait" ? "line-through text-muted-foreground" : ""}>
                          {t.nom}
                        </span>
                        {t.priorite && (
                          <Badge variant="outline" className="text-[10px] ml-auto">{t.priorite}</Badge>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="space-y-2">
                <p className="text-xs font-semibold text-muted-foreground uppercase">Actions</p>
                <Button variant="outline" size="sm" asChild className="w-full">
                  <a href={`/maison/projets?id=${projet.id}`} onClick={onFermer}>
                    ✏️ Ouvrir le projet complet
                  </a>
                </Button>
                {projet.statut === "planifie" && (
                  <p className="text-xs text-muted-foreground">
                    💡 Marquez ce projet &quot;en cours&quot; une fois démarré
                  </p>
                )}
              </div>
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
