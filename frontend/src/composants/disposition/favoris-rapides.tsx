// ═══════════════════════════════════════════════════════════
// Favoris rapides — Pages épinglées par l'utilisateur
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Star, X } from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { Button } from "@/composants/ui/button";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";

interface Favori {
  nom: string;
  chemin: string;
}

interface FavorisRapidesProps {
  collapsed: boolean;
}

/**
 * Liste des favoris en haut de sidebar — permet d'épingler pages fréquentes.
 */
export function FavorisRapides({ collapsed }: FavorisRapidesProps) {
  const pathname = usePathname();
  const [favoris, setFavoris] = utiliserStockageLocal<Favori[]>("favoris-pages", []);
  const [survol, setSurvol] = useState<string | null>(null);

  const retirerFavori = (chemin: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setFavoris((prev) => prev.filter((f) => f.chemin !== chemin));
  };

  if (favoris.length === 0) {
    return null;
  }

  return (
    <div className="px-3 py-2 space-y-1">
      {!collapsed && (
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
          Favoris
        </p>
      )}
      {favoris.map((favori) => {
        const estActif = pathname === favori.chemin;
        const enSurvol = survol === favori.chemin;

        return (
          <Link
            key={favori.chemin}
            href={favori.chemin}
            className={cn(
              "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors relative group",
              estActif
                ? "bg-accent text-accent-foreground"
                : "hover:bg-accent/50 text-foreground"
            )}
            onMouseEnter={() => setSurvol(favori.chemin)}
            onMouseLeave={() => setSurvol(null)}
          >
            <Star
              className={cn(
                "h-4 w-4 flex-shrink-0",
                estActif ? "fill-current text-yellow-500" : "fill-current text-yellow-400"
              )}
            />
            {!collapsed && (
              <>
                <span className="truncate flex-1">{favori.nom}</span>
                {enSurvol && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5 opacity-60 hover:opacity-100"
                    onClick={(e) => retirerFavori(favori.chemin, e)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                )}
              </>
            )}
          </Link>
        );
      })}
    </div>
  );
}

/**
 * Hook pour ajouter/retirer favori depuis n'importe quelle page.
 */
export function utiliserFavoris() {
  const [favoris, setFavoris] = utiliserStockageLocal<Favori[]>("favoris-pages", []);

  const estFavori = (chemin: string) => {
    return favoris.some((f) => f.chemin === chemin);
  };

  const ajouterFavori = (nom: string, chemin: string) => {
    if (!estFavori(chemin)) {
      setFavoris((prev) => [...prev, { nom, chemin }]);
    }
  };

  const retirerFavori = (chemin: string) => {
    setFavoris((prev) => prev.filter((f) => f.chemin !== chemin));
  };

  const basculerFavori = (nom: string, chemin: string) => {
    if (estFavori(chemin)) {
      retirerFavori(chemin);
    } else {
      ajouterFavori(nom, chemin);
    }
  };

  return {
    favoris,
    estFavori,
    ajouterFavori,
    retirerFavori,
    basculerFavori,
  };
}
