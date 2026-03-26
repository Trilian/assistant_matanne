// ═══════════════════════════════════════════════════════════
// Fil d'ariane — Breadcrumbs sous-pages
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";
import { BoutonEpingler } from "./bouton-epingler";
import { TooltipProvider } from "@/composants/ui/tooltip";

/** Traduit un segment d'URL en libellé français */
function traduireSegment(segment: string): string {
  const traductions: Record<string, string> = {
    cuisine: "Cuisine",
    recettes: "Recettes",
    planning: "Planning",
    courses: "Courses",
    inventaire: "Inventaire",
    "batch-cooking": "Batch Cooking",
    "anti-gaspillage": "Anti-Gaspillage",
    famille: "Famille",
    jules: "Jules",
    activites: "Activités",
    routines: "Routines",
    budget: "Budget",
    weekend: "Weekend",
    anniversaires: "Anniversaires",
    contacts: "Contacts",
    journal: "Journal",
    documents: "Documents",
    maison: "Maison",
    projets: "Projets",
    jardin: "Jardin",
    entretien: "Entretien",
    charges: "Charges",
    depenses: "Dépenses",
    energie: "Énergie",
    stocks: "Stocks",
    cellier: "Cellier",
    artisans: "Artisans",
    contrats: "Contrats",
    garanties: "Garanties",
    diagnostics: "Diagnostics",
    visualisation: "Visualisation",
    "eco-tips": "Éco-Tips",
    jeux: "Jeux",
    paris: "Paris",
    loto: "Loto",
    euromillions: "EuroMillions",
    outils: "Outils",
    "chat-ia": "Chat IA",
    convertisseur: "Convertisseur",
    meteo: "Météo",
    minuteur: "Minuteur",
    notes: "Notes",
    parametres: "Paramètres",
    nouveau: "Nouveau",
    timeline: "Timeline",
  };
  return traductions[segment] ?? segment;
}

/**
 * Fil d'ariane généré automatiquement depuis l'URL courante.
 * Masqué sur la page d'accueil. Chaque segment est traduit en français via `traduireSegment`.
 */
export function FilAriane() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  // Pas de fil d'ariane sur l'accueil
  if (segments.length === 0) return null;

  return (
    <TooltipProvider>
      <nav aria-label="Fil d'Ariane" className="flex items-center gap-1 text-sm text-muted-foreground px-4 md:px-6 py-2">
        <Link href="/" className="hover:text-foreground transition-colors" aria-label="Accueil">
          <Home className="h-4 w-4" />
        </Link>
        {segments.map((segment, index) => {
          const chemin = "/" + segments.slice(0, index + 1).join("/");
          const estDernier = index === segments.length - 1;

          return (
            <span key={chemin} className="flex items-center gap-1">
              <ChevronRight className="h-3 w-3" />
              {estDernier ? (
                <span className="font-medium text-foreground">
                  {traduireSegment(segment)}
                </span>
              ) : (
                <Link
                  href={chemin}
                  className="hover:text-foreground transition-colors"
                >
                  {traduireSegment(segment)}
                </Link>
              )}
            </span>
          );
        })}
        
        {/* Bouton épingler page */}
        <div className="ml-auto">
          <BoutonEpingler />
        </div>
      </nav>
    </TooltipProvider>
  );
}
