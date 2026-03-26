// ═══════════════════════════════════════════════════════════
// Bouton épingler — Ajouter/retirer page actuelle des favoris
// ═══════════════════════════════════════════════════════════

"use client";

import { Star } from "lucide-react";
import { usePathname } from "next/navigation";
import { Button } from "@/composants/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/composants/ui/tooltip";
import { utiliserFavoris } from "./favoris-rapides";
import { cn } from "@/bibliotheque/utils";
import { NOMS_PAGES } from "@/bibliotheque/pages-navigation";

/**
 * Bouton pour épingler/désépingler la page actuelle aux favoris.
 */
export function BoutonEpingler() {
  const pathname = usePathname();
  const { estFavori, basculerFavori } = utiliserFavoris();

  // Ne pas afficher sur pages sans nom (détails, création)
  const nomPage = NOMS_PAGES[pathname];
  if (!nomPage) {
    return null;
  }

  const favori = estFavori(pathname);

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={() => basculerFavori(nomPage, pathname)}
          aria-label={favori ? "Retirer des favoris" : "Ajouter aux favoris"}
        >
          <Star
            className={cn(
              "h-4 w-4 transition-colors",
              favori
                ? "fill-yellow-400 text-yellow-400"
                : "text-muted-foreground hover:text-yellow-400"
            )}
          />
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        {favori ? "Retirer des favoris" : "Ajouter aux favoris"}
      </TooltipContent>
    </Tooltip>
  );
}
