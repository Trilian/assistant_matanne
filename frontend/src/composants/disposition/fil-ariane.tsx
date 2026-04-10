// ═══════════════════════════════════════════════════════════
// Fil d'ariane — Breadcrumbs sous-pages
// ═══════════════════════════════════════════════════════════

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";
import { BoutonEpingler } from "./bouton-epingler";
import { TooltipProvider } from "@/composants/ui/tooltip";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { getModuleThemeClass, obtenirMetaModule, obtenirModuleDepuisPathname } from "@/bibliotheque/theme-modules";
import { cn } from "@/bibliotheque/utils";

/** Retourne true si le segment ressemble à un ID dynamique (numérique ou UUID) */
function estSegmentDynamique(segment: string): boolean {
  return /^\d+$/.test(segment) || /^[0-9a-f]{8}-[0-9a-f-]{27}$/.test(segment);
}

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
    "vision-maison": "Vision Maison",
    scenarios: "Scénarios",
    "veille-immo": "Veille Immo",
    marche: "Marché",
    deco: "Déco",
  };
  return traductions[segment] ?? segment;
}

/**
 * Fil d'ariane généré automatiquement depuis l'URL courante.
 * Masqué sur la page d'accueil. Chaque segment est traduit en français via `traduireSegment`.
 */
export function FilAriane() {
  const pathname = usePathname();
  const moduleActif = obtenirModuleDepuisPathname(pathname);
  const metaModule = obtenirMetaModule(moduleActif);
  const segments = pathname.split("/").filter(Boolean);
  const { titrePage } = utiliserStoreUI();

  // Pas de fil d'ariane sur l'accueil
  if (segments.length === 0) return null;

  return (
    <TooltipProvider>
      <nav
        aria-label="Fil d'Ariane"
        className={cn(
          "flex items-center gap-1 px-4 py-2 text-sm text-muted-foreground md:px-6",
          getModuleThemeClass(moduleActif)
        )}
      >
        <Link href="/" className="hover:text-foreground transition-colors" aria-label="Accueil">
          <Home className="h-4 w-4" />
        </Link>
        {segments.map((segment, index) => {
          const chemin = "/" + segments.slice(0, index + 1).join("/");
          const estDernier = index === segments.length - 1;

          return (
            <span key={chemin} className="flex items-center gap-1">
              <ChevronRight className="h-3 w-3" />
              <Link
                href={chemin}
                aria-current={estDernier ? "page" : undefined}
                className={cn(
                  estDernier
                    ? "font-medium module-accent-text"
                    : "hover:text-foreground transition-colors",
                  estDernier && getModuleThemeClass(moduleActif)
                )}
              >
                {estSegmentDynamique(segment) && titrePage
                  ? titrePage
                  : traduireSegment(segment)}
              </Link>
            </span>
          );
        })}
        
        <div className="ml-auto flex items-center gap-2">
          <span className="hidden rounded-full border px-2 py-0.5 text-[11px] font-medium md:inline-flex module-accent-bg module-accent-text module-accent-border">
            {`Module actif : ${metaModule.label}`}
          </span>
          <BoutonEpingler />
        </div>
      </nav>
    </TooltipProvider>
  );
}
