// ═══════════════════════════════════════════════════════════
// DrawerFicheTache — Fiche détaillée d'une tâche ménagère
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/composants/ui/sheet";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { obtenirFicheTache, genererFicheTacheIA, type FicheTache } from "@/bibliotheque/api/maison";

const DIFF_COULEUR: Record<string, string> = {
  facile: "bg-green-100 text-green-800",
  moyen: "bg-yellow-100 text-yellow-800",
  difficile: "bg-red-100 text-red-800",
};

interface DrawerFicheTacheProps {
  ouvert: boolean;
  onFermer: () => void;
  typeTache: string;
  nomTache: string;
  idTache?: string | number;
}

export function DrawerFicheTache({
  ouvert,
  onFermer,
  typeTache,
  nomTache,
  idTache,
}: DrawerFicheTacheProps) {
  const [fiche, setFiche] = useState<FicheTache | null>(null);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const chargerFiche = async () => {
    setChargement(true);
    setErreur(null);
    try {
      const data = await obtenirFicheTache({
        type_tache: typeTache,
        id_tache: idTache,
        nom_tache: nomTache,
      });
      setFiche(data);
    } catch {
      // Essayer de générer avec l'IA
      try {
        const data = await genererFicheTacheIA(nomTache);
        setFiche(data);
      } catch {
        setErreur("Fiche non disponible pour cette tâche");
      }
    } finally {
      setChargement(false);
    }
  };

  // Charger la fiche à l'ouverture
  const handleOpenChange = (open: boolean) => {
    if (open && !fiche && !chargement) {
      chargerFiche();
    }
    if (!open) onFermer();
  };

  return (
    <Sheet open={ouvert} onOpenChange={handleOpenChange}>
      <SheetContent side="right" className="w-full sm:w-[480px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{nomTache}</SheetTitle>
          <SheetDescription>Guide étape par étape</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {chargement && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          )}

          {erreur && (
            <div className="text-sm text-muted-foreground text-center py-8">
              <p>{erreur}</p>
              <Button variant="outline" size="sm" onClick={chargerFiche} className="mt-3">
                Réessayer
              </Button>
            </div>
          )}

          {fiche && !chargement && (
            <>
              {/* En-tête fiche */}
              <div className="flex items-center gap-3 flex-wrap">
                <span
                  className={`text-xs font-medium px-2 py-0.5 rounded-full ${DIFF_COULEUR[fiche.difficulte] ?? "bg-muted"}`}
                >
                  {fiche.difficulte}
                </span>
                <span className="text-sm text-muted-foreground">
                  ⏱ {fiche.duree_estimee_min} min
                </span>
                {fiche.source && (
                  <span className="text-xs text-muted-foreground">
                    📚 {fiche.source}
                  </span>
                )}
              </div>

              {/* Étapes */}
              {fiche.etapes.length > 0 && (
                <div>
                  <h3 className="font-semibold text-sm mb-3">Étapes</h3>
                  <ol className="space-y-3">
                    {fiche.etapes.map((etape, i) => (
                      <li key={i} className="flex gap-3">
                        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center">
                          {i + 1}
                        </span>
                        <span className="text-sm leading-relaxed pt-0.5">{etape}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Produits */}
              {fiche.produits.length > 0 && (
                <div>
                  <h3 className="font-semibold text-sm mb-2">Produits</h3>
                  <div className="flex flex-wrap gap-2">
                    {fiche.produits.map((p) => (
                      <Badge key={p} variant="secondary">
                        🧴 {p}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Outils */}
              {fiche.outils.length > 0 && (
                <div>
                  <h3 className="font-semibold text-sm mb-2">Outils</h3>
                  <div className="flex flex-wrap gap-2">
                    {fiche.outils.map((o) => (
                      <Badge key={o} variant="outline">
                        🔧 {o}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Astuce connectée */}
              {fiche.astuce_connectee && (
                <div className="rounded-lg bg-blue-50 dark:bg-blue-950/30 p-4">
                  <p className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
                    💡 Astuce domotique
                  </p>
                  <p className="text-sm text-blue-600 dark:text-blue-400">
                    {fiche.astuce_connectee}
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
