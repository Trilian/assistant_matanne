// ═══════════════════════════════════════════════════════════
// Barre latérale — Navigation desktop avec sous-menus
// ═══════════════════════════════════════════════════════════

"use client";

import { createElement, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { PAGES_NAVIGATION, type PageNavigation } from "@/bibliotheque/pages-navigation";
import {
  Home,
  ChefHat,
  Users,
  House,
  Gamepad2,
  PanelLeftClose,
  PanelLeft,
  ChevronDown,
  BookOpen,
  CalendarDays,
  ShoppingCart,
  Package,
  CookingPot,
  Baby,
  ClipboardList,
  RotateCw,
  Wallet,
  Hammer,
  Sprout,
  SprayCan,
  Banknote,
  FileText,
  Trophy,
  Dices,
  TrendingUp,
  Cake,
  Contact,
  Layers,
  Plane,
  Activity,
  CalendarRange,
  Boxes,
  ShoppingBag,
  Settings,
  Wrench,
  ClipboardCheck,
  Map,
  Lightbulb,
  Zap,
} from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { utiliserBadgesModules } from "@/crochets/utiliser-badges-modules";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Separator } from "@/composants/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/composants/ui/tooltip";
import { FavorisRapides } from "./favoris-rapides";
import { getModuleThemeClass, obtenirModuleDepuisPathname } from "@/bibliotheque/theme-modules";

interface CategorieNav {
  label: string;
  debut: number;
  fin: number;
}

interface SousLien {
  nom: string;
  chemin: string;
  Icone: React.ElementType;
}

interface LienNav {
  nom: string;
  chemin: string;
  Icone: React.ElementType;
  sousLiens?: SousLien[];
  categories?: CategorieNav[];
}

const LIENS: LienNav[] = [
  { nom: "Accueil", chemin: "/", Icone: Home },
  { nom: "Ma Journée", chemin: "/ma-journee", Icone: CalendarDays },
  { nom: "Focus", chemin: "/focus", Icone: Zap },
  { nom: "Widget Tablette", chemin: "/widget-tablette", Icone: Lightbulb },
  { nom: "Ma Semaine", chemin: "/ma-semaine", Icone: CalendarRange },
  {
    nom: "Cuisine",
    chemin: "/cuisine",
    Icone: ChefHat,
    sousLiens: [
      { nom: "Ma Semaine", chemin: "/cuisine/ma-semaine", Icone: CalendarDays },
      { nom: "Recettes", chemin: "/cuisine/recettes", Icone: BookOpen },
      { nom: "Courses", chemin: "/cuisine/courses", Icone: ShoppingCart },
      { nom: "Frigo & Stock", chemin: "/cuisine/inventaire", Icone: Package },
      { nom: "Batch Cooking", chemin: "/cuisine/batch-cooking", Icone: CookingPot },
    ],
  },
  {
    nom: "Famille",
    chemin: "/famille",
    Icone: Users,
    sousLiens: [
      // 👶 Enfant
      { nom: "Jules", chemin: "/famille/jules", Icone: Baby },
      { nom: "Activités", chemin: "/famille/activites", Icone: ClipboardList },
      { nom: "Routines", chemin: "/famille/routines", Icone: RotateCw },
      // 💰 Budget & Achats
      { nom: "Budget", chemin: "/famille/budget", Icone: Wallet },
      { nom: "Achats", chemin: "/famille/achats", Icone: ShoppingBag },
      // 📅 Événements
      { nom: "Anniversaires", chemin: "/famille/anniversaires", Icone: Cake },
      { nom: "Voyages", chemin: "/famille/voyages", Icone: Plane },
      // 📋 Organisation
      { nom: "Contacts", chemin: "/famille/contacts", Icone: Contact },
      { nom: "Documents", chemin: "/famille/documents", Icone: FileText },
      { nom: "Garmin", chemin: "/famille/garmin", Icone: Activity },
      { nom: "Config", chemin: "/famille/config", Icone: Settings },
    ],
    // Catégories pour regroupement visuel des sous-liens
    categories: [
      { label: "Enfant", debut: 0, fin: 3 },
      { label: "Budget & Achats", debut: 3, fin: 5 },
      { label: "Événements", debut: 5, fin: 7 },
      { label: "Organisation", debut: 7, fin: 11 },
    ],
  },
  {
    nom: "Maison",
    chemin: "/maison",
    Icone: House,
    sousLiens: [
      // 🏠 Habitat
      { nom: "Visualisation", chemin: "/maison/visualisation", Icone: Layers },
      { nom: "Ménage", chemin: "/maison/menage", Icone: SprayCan },
      { nom: "Jardin", chemin: "/maison/jardin", Icone: Sprout },
      // 🔧 Travaux & Équipements
      { nom: "Travaux", chemin: "/maison/travaux", Icone: Hammer },
      { nom: "Équipements", chemin: "/maison/equipements", Icone: Boxes },
      { nom: "Artisans", chemin: "/maison/artisans", Icone: Wrench },
      { nom: "Diagnostics", chemin: "/maison/diagnostics", Icone: ClipboardCheck },
      // 💼 Admin & Finances
      { nom: "Finances", chemin: "/maison/finances", Icone: Banknote },
      { nom: "Abonnements", chemin: "/maison/abonnements", Icone: FileText },
      { nom: "Provisions", chemin: "/maison/provisions", Icone: Package },
      { nom: "Documents", chemin: "/maison/documents", Icone: FileText },
    ],
    categories: [
      { label: "Habitat", debut: 0, fin: 3 },
      { label: "Travaux & Équipements", debut: 3, fin: 7 },
      { label: "Admin & Finances", debut: 7, fin: 11 },
    ],
  },
  {
    nom: "Habitat",
    chemin: "/habitat",
    Icone: Map,
    sousLiens: [
      { nom: "Scenarios", chemin: "/habitat/scenarios", Icone: Home },
      { nom: "Veille Immo", chemin: "/habitat/veille-immo", Icone: ShoppingBag },
      { nom: "Marche", chemin: "/habitat/marche", Icone: TrendingUp },
      { nom: "Plans", chemin: "/habitat/plans", Icone: Layers },
      { nom: "Deco", chemin: "/habitat/deco", Icone: House },
      { nom: "Jardin", chemin: "/habitat/jardin", Icone: Sprout },
    ],
  },
  {
    nom: "Jeux",
    chemin: "/jeux",
    Icone: Gamepad2,
    sousLiens: [
      { nom: "Paris", chemin: "/jeux/paris", Icone: Trophy },
      { nom: "Loto", chemin: "/jeux/loto", Icone: Dices },
      { nom: "EuroMillions", chemin: "/jeux/euromillions", Icone: Dices },
      { nom: "Bankroll", chemin: "/jeux/bankroll", Icone: TrendingUp },
      { nom: "Performance", chemin: "/jeux/performance", Icone: TrendingUp },
    ],
  },
];

/**
 * Barre latérale de navigation desktop — rétractable, avec sous-menus accordéon.
 * La section active est automatiquement ouverte au chargement.
 */
export function BarreLaterale() {
  const pathname = usePathname();
  const router = useRouter();
  const { sidebarOuverte, basculerSidebar } = utiliserStoreUI();

  const { badges } = utiliserBadgesModules();

  const [sectionsOuvertes, setSectionsOuvertes] = useState<Set<string>>(() => {
    // Charger les sections sauvegardées depuis localStorage
    const saved: string[] = (() => {
      try {
        return typeof window !== "undefined"
          ? (JSON.parse(window.localStorage.getItem("nav-sections-ouvertes") ?? "[]") as string[])
          : [];
      } catch {
        return [];
      }
    })();
    const initial = new Set<string>(saved);
    // Toujours ouvrir la section active courante
    for (const lien of LIENS) {
      if (lien.sousLiens && pathname.startsWith(lien.chemin) && lien.chemin !== "/") {
        initial.add(lien.chemin);
      }
    }
    return initial;
  });

  const basculerSection = (chemin: string) => {
    setSectionsOuvertes((prev) => {
      const next = new Set(prev);
      if (next.has(chemin)) next.delete(chemin);
      else next.add(chemin);
      // Persister dans localStorage
      try {
        window.localStorage.setItem("nav-sections-ouvertes", JSON.stringify([...next]));
      } catch {}
      return next;
    });
  };

  // Section Récents : top 3 depuis l'historique Ctrl+K
  const [historiqueChemins] = utiliserStockageLocal<string[]>("command-history", []);
  const recents = useMemo((): PageNavigation[] => {
    return historiqueChemins
      .map((chemin) => PAGES_NAVIGATION.find((p) => p.chemin === chemin))
      .filter((p): p is PageNavigation => p !== undefined)
      .slice(0, 3);
  }, [historiqueChemins]);

  const prefetchRoute = (chemin: string) => {
    router.prefetch(chemin);
  };

  const classeModule = (chemin: string) => getModuleThemeClass(obtenirModuleDepuisPathname(chemin));
  const obtenirBadgeNavigation = (chemin: string) => {
    if (chemin === "/cuisine") return badges.cuisine;
    if (chemin === "/famille") return badges.famille;
    if (chemin === "/maison") return badges.maison;
    if (chemin === "/jeux") return badges.jeux;
    return 0;
  };
  const formaterBadge = (valeur: number) => (valeur > 9 ? "9+" : String(valeur));

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300",
        sidebarOuverte ? "w-56" : "w-16"
      )}
    >
      {/* Logo / Titre */}
            <div className="flex h-14 items-center gap-2 border-b px-4">
        <span className="text-lg" role="img" aria-label="Accueil">🏠</span>
        {sidebarOuverte && (
          <span className="font-semibold text-sm truncate">
            Assistant Matanne
          </span>
        )}
        <Button
          variant="ghost"
          size="icon"
          className="ml-auto h-8 w-8"
          onClick={basculerSidebar}
          aria-label={sidebarOuverte ? "Réduire la barre latérale" : "Ouvrir la barre latérale"}
        >
          {sidebarOuverte ? (
            <PanelLeftClose className="h-4 w-4" />
          ) : (
            <PanelLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Favoris rapides */}
      <FavorisRapides collapsed={!sidebarOuverte} />

      {/* Récents (Idée C) — visible uniquement quand la sidebar est élargie */}
      {sidebarOuverte && recents.length > 0 && (
        <>
          <Separator className="mx-3" />
          <div className="px-3 py-2 space-y-1">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
              Récents
            </p>
            {recents.map((page) => {
              const IconePage = page.Icone as React.ElementType;
              const estActif = pathname === page.chemin;
              return (
                <Link
                  key={page.chemin}
                  href={page.chemin}
                  onMouseEnter={() => prefetchRoute(page.chemin)}
                  onFocus={() => prefetchRoute(page.chemin)}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
                    estActif
                      ? "bg-accent text-accent-foreground"
                      : "hover:bg-accent/50 text-foreground/70"
                  )}
                >
                  {createElement(IconePage, { className: "h-4 w-4 shrink-0 text-muted-foreground" })}
                  <span className="truncate">{page.nom}</span>
                </Link>
              );
            })}
          </div>
        </>
      )}
      {sidebarOuverte && recents.length === 0 && <Separator className="mx-3" />}

      {/* Navigation */}
      <nav aria-label="Navigation principale" className="flex-1 overflow-y-auto space-y-1 p-2">
        {LIENS.map((lien) => {
          const IconeLien = lien.Icone as React.ElementType;
          const estActif =
            lien.chemin === "/"
              ? pathname === "/"
              : pathname.startsWith(lien.chemin);
          const aSousliens = lien.sousLiens && lien.sousLiens.length > 0;
          const estOuverte = sectionsOuvertes.has(lien.chemin);

          const nbBadge = obtenirBadgeNavigation(lien.chemin);

          const boutonPrincipal = (
            <div className="flex items-center">
              <Link
                href={lien.chemin}
                onMouseEnter={() => prefetchRoute(lien.chemin)}
                onFocus={() => prefetchRoute(lien.chemin)}
                className={cn(
                  "flex flex-1 items-center gap-3 rounded-md border border-transparent px-3 py-2 text-sm font-medium transition-colors",
                  classeModule(lien.chemin),
                  estActif
                    ? "module-accent-bg module-accent-text module-accent-border"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                )}
              >
                <span className="relative shrink-0">
                  {createElement(IconeLien, { className: "h-5 w-5 shrink-0" })}
                  {!sidebarOuverte && nbBadge > 0 && (
                    <span className="absolute -right-1 -top-1 h-2.5 w-2.5 rounded-full border-2 border-background bg-destructive" />
                  )}
                </span>
                {sidebarOuverte && <span className="truncate" title={lien.nom}>{lien.nom}</span>}
                {sidebarOuverte && nbBadge > 0 && (
                  <Badge variant={lien.chemin === "/famille" ? "destructive" : "secondary"} className="ml-auto h-5 min-w-5 px-1 text-xs flex items-center justify-center shrink-0">
                    {formaterBadge(nbBadge)}
                  </Badge>
                )}
              </Link>
              {sidebarOuverte && aSousliens && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    basculerSection(lien.chemin);
                  }}
                  className="p-1 rounded hover:bg-sidebar-accent/50 text-sidebar-foreground/50"
                  aria-label={estOuverte ? `Fermer le sous-menu ${lien.nom}` : `Ouvrir le sous-menu ${lien.nom}`}
                >
                  <ChevronDown
                    className={cn(
                      "h-4 w-4 transition-transform",
                      estOuverte && "rotate-180"
                    )}
                  />
                </button>
              )}
            </div>
          );

          if (!sidebarOuverte) {
            return (
              <Tooltip key={lien.chemin}>
                <TooltipTrigger asChild>{boutonPrincipal}</TooltipTrigger>
                <TooltipContent side="right">{lien.nom}</TooltipContent>
              </Tooltip>
            );
          }

          return (
            <div key={lien.chemin}>
              {boutonPrincipal}
              {/* Sous-liens avec groupage optionnel par catégories */}
              {aSousliens && estOuverte && sidebarOuverte && (
                <div className="ml-5 mt-1 space-y-0.5 border-l pl-3">
                  {lien.categories && lien.categories.length > 0
                    ? // Affichage groupé par catégories
                      lien.categories.map((categorie) => {
                        const sousLiensCategorie = lien.sousLiens!.slice(
                          categorie.debut,
                          categorie.fin
                        );
                        return (
                          <div key={categorie.label}>
                            {/* Label de catégorie */}
                            <p className="text-xs font-semibold text-sidebar-foreground/40 uppercase tracking-wider px-2 py-1 mt-2 first:mt-0">
                              {categorie.label}
                            </p>
                            {/* Sous-liens de la catégorie */}
                            {sousLiensCategorie.map((sous) => {
                              const IconeSousLien = sous.Icone as React.ElementType;
                              const sousActif = pathname === sous.chemin;
                              return (
                                <Link
                                  key={sous.chemin}
                                  href={sous.chemin}
                                  onMouseEnter={() => prefetchRoute(sous.chemin)}
                                  onFocus={() => prefetchRoute(sous.chemin)}
                                  aria-label={sous.nom}
                                  className={cn(
                                    "flex items-center gap-2 rounded-md border border-transparent px-2 py-1.5 text-xs transition-colors",
                                    classeModule(sous.chemin),
                                    sousActif
                                      ? "module-accent-bg module-accent-text module-accent-border font-medium"
                                      : "text-sidebar-foreground/60 hover:bg-sidebar-accent/40 hover:text-sidebar-accent-foreground"
                                  )}
                                >
                                  {createElement(IconeSousLien, { className: "h-3.5 w-3.5 shrink-0" })}
                                  <span className="truncate">{sous.nom}</span>
                                </Link>
                              );
                            })}
                          </div>
                        );
                      })
                    : // Affichage sans catégories (défaut)
                      lien.sousLiens!.map((sous) => {
                        const IconeSousLien = sous.Icone as React.ElementType;
                        const sousActif = pathname === sous.chemin;
                        return (
                          <Link
                            key={sous.chemin}
                            href={sous.chemin}
                            onMouseEnter={() => prefetchRoute(sous.chemin)}
                            onFocus={() => prefetchRoute(sous.chemin)}
                            aria-label={sous.nom}
                            className={cn(
                              "flex items-center gap-2 rounded-md border border-transparent px-2 py-1.5 text-xs transition-colors",
                              classeModule(sous.chemin),
                              sousActif
                                ? "module-accent-bg module-accent-text module-accent-border font-medium"
                                : "text-sidebar-foreground/60 hover:bg-sidebar-accent/40 hover:text-sidebar-accent-foreground"
                            )}
                          >
                            {createElement(IconeSousLien, { className: "h-3.5 w-3.5 shrink-0" })}
                            <span className="truncate">{sous.nom}</span>
                          </Link>
                        );
                      })}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* Séparateur bas — l’accès admin reste disponible via URL directe et Ctrl+Shift+A */}
      <Separator />
      <div className="p-2 space-y-0.5" />
    </aside>
  );
}
