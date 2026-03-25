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

// Map des chemins vers leurs noms lisibles
const NOMS_PAGES: Record<string, string> = {
  "/": "Accueil",
  "/cuisine": "Cuisine",
  "/cuisine/recettes": "Recettes",
  "/cuisine/planning": "Planning Repas",
  "/cuisine/ma-semaine": "Ma Semaine",
  "/cuisine/courses": "Courses",
  "/cuisine/inventaire": "Inventaire",
  "/cuisine/batch-cooking": "Batch Cooking",
  "/cuisine/anti-gaspillage": "Anti-Gaspillage",
  "/cuisine/photo-frigo": "Photo Frigo",
  "/famille": "Famille",
  "/famille/jules": "Jules",
  "/famille/activites": "Activités",
  "/famille/routines": "Routines",
  "/famille/budget": "Budget Famille",
  "/famille/weekend": "Weekend",
  "/famille/anniversaires": "Anniversaires",
  "/famille/contacts": "Contacts",
  "/famille/journal": "Journal",
  "/famille/documents": "Documents",
  "/maison": "Maison",
  "/maison/projets": "Projets",
  "/maison/menage": "Ménage",
  "/maison/jardin": "Jardin",
  "/maison/entretien": "Entretien",
  "/maison/domotique": "Domotique",
  "/maison/charges": "Charges",
  "/maison/depenses": "Dépenses",
  "/maison/energie": "Énergie",
  "/maison/stocks": "Stocks",
  "/maison/cellier": "Cellier",
  "/maison/artisans": "Artisans",
  "/maison/contrats": "Contrats",
  "/maison/garanties": "Garanties",
  "/maison/diagnostics": "Diagnostics",
  "/maison/visualisation": "Visualisation",
  "/maison/eco-tips": "Éco-Tips",
  "/jeux": "Jeux",
  "/jeux/paris": "Paris Sportifs",
  "/jeux/loto": "Loto",
  "/jeux/euromillions": "EuroMillions",
  "/jeux/performance": "Performance",
  "/jeux/responsable": "Jeu Responsable",
  "/outils": "Outils",
  "/outils/chat-ia": "Chat IA",
  "/outils/convertisseur": "Convertisseur",
  "/outils/meteo": "Météo",
  "/outils/minuteur": "Minuteur",
  "/outils/notes": "Notes",
  "/outils/nutritionniste": "Nutritionniste",
  "/parametres": "Paramètres",
  "/planning": "Planning",
};

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
