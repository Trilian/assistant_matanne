// ═══════════════════════════════════════════════════════════
// Barre latérale — Navigation desktop avec sous-menus
// ═══════════════════════════════════════════════════════════

"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { PAGES_NAVIGATION, type PageNavigation } from "@/bibliotheque/pages-navigation";
import {
  Home,
  ChefHat,
  Users,
  Calendar,
  House,
  Gamepad2,
  Wrench,
  PanelLeftClose,
  PanelLeft,
  ChevronDown,
  BookOpen,
  CalendarDays,
  ShoppingCart,
  Package,
  CookingPot,
  Leaf,
  Baby,
  ClipboardList,
  RotateCw,
  Wallet,
  Hammer,
  Sprout,
  SprayCan,
  Receipt,
  Banknote,
  Zap,
  Wine,
  FileText,
  ShieldCheck,
  ClipboardCheck,
  Trophy,
  Dices,
  TrendingUp,
  Cake,
  Contact,
  Layers,
  Shield,
  Camera,
  Wifi,
  CalendarRange,
  Boxes,
  ShoppingBag,
  Settings,
} from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { evaluerRappelsFamille } from "@/bibliotheque/api/famille";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Separator } from "@/composants/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/composants/ui/tooltip";
import { FavorisRapides } from "./favoris-rapides";
import type { RappelFamille } from "@/types/famille";

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
}

const LIENS: LienNav[] = [
  { nom: "Accueil", chemin: "/", Icone: Home },
  { nom: "Ma Semaine", chemin: "/ma-semaine", Icone: CalendarRange },
  {
    nom: "Cuisine",
    chemin: "/cuisine",
    Icone: ChefHat,
    sousLiens: [
      { nom: "Recettes", chemin: "/cuisine/recettes", Icone: BookOpen },
      { nom: "Planning", chemin: "/cuisine/planning", Icone: CalendarDays },
      { nom: "Courses", chemin: "/cuisine/courses", Icone: ShoppingCart },
      { nom: "Inventaire", chemin: "/cuisine/inventaire", Icone: Package },
      { nom: "Batch Cooking", chemin: "/cuisine/batch-cooking", Icone: CookingPot },
      { nom: "Anti-Gaspi", chemin: "/cuisine/anti-gaspillage", Icone: Leaf },
      { nom: "Photo Frigo", chemin: "/cuisine/photo-frigo", Icone: Camera },
    ],
  },
  {
    nom: "Famille",
    chemin: "/famille",
    Icone: Users,
    sousLiens: [
      { nom: "Jules", chemin: "/famille/jules", Icone: Baby },
      { nom: "Activités", chemin: "/famille/activites", Icone: ClipboardList },
      { nom: "Routines", chemin: "/famille/routines", Icone: RotateCw },
      { nom: "Budget", chemin: "/famille/budget", Icone: Wallet },
      { nom: "Achats", chemin: "/famille/achats", Icone: ShoppingBag },
      { nom: "Anniversaires", chemin: "/famille/anniversaires", Icone: Cake },
      { nom: "Contacts", chemin: "/famille/contacts", Icone: Contact },
      { nom: "Documents", chemin: "/famille/documents", Icone: FileText },
      { nom: "Config", chemin: "/famille/config", Icone: Settings },
    ],
  },
  {
    nom: "Maison",
    chemin: "/maison",
    Icone: House,
    sousLiens: [
      { nom: "Visualisation", chemin: "/maison/visualisation", Icone: Layers },
      { nom: "Ménage", chemin: "/maison/menage", Icone: SprayCan },
      { nom: "Jardin", chemin: "/maison/jardin", Icone: Sprout },
      { nom: "Travaux", chemin: "/maison/travaux", Icone: Hammer },
      { nom: "Équipements", chemin: "/maison/equipements", Icone: Boxes },
      { nom: "Finances", chemin: "/maison/finances", Icone: Banknote },
      { nom: "Provisions", chemin: "/maison/provisions", Icone: Package },
      { nom: "Documents", chemin: "/maison/documents", Icone: FileText },
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
      { nom: "Performance", chemin: "/jeux/performance", Icone: TrendingUp },
      { nom: "Jeu responsable", chemin: "/jeux/responsable", Icone: Shield },
    ],
  },
];

/**
 * Barre latérale de navigation desktop — rétractable, avec sous-menus accordéon.
 * La section active est automatiquement ouverte au chargement.
 */
export function BarreLaterale() {
  const pathname = usePathname();
  const { sidebarOuverte, basculerSidebar } = utiliserStoreUI();
  const { utilisateur } = utiliserAuth();
  const estAdmin = utilisateur?.role === "admin";

  const { data: rappelsData } = utiliserRequete<{ rappels: RappelFamille[]; total: number }>(
    ["famille", "rappels", "badge"],
    evaluerRappelsFamille,
    { staleTime: 5 * 60 * 1000, refetchInterval: 10 * 60 * 1000 }
  );
  const nbRappelsDanger = rappelsData?.rappels?.filter((r) => r.priorite === "danger").length ?? 0;

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
              const estActif = pathname === page.chemin;
              return (
                <Link
                  key={page.chemin}
                  href={page.chemin}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
                    estActif
                      ? "bg-accent text-accent-foreground"
                      : "hover:bg-accent/50 text-foreground/70"
                  )}
                >
                  <page.Icone className="h-4 w-4 shrink-0 text-muted-foreground" />
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
          const estActif =
            lien.chemin === "/"
              ? pathname === "/"
              : pathname.startsWith(lien.chemin);
          const aSousliens = lien.sousLiens && lien.sousLiens.length > 0;
          const estOuverte = sectionsOuvertes.has(lien.chemin);

          const boutonPrincipal = (
            <div className="flex items-center">
              <Link
                href={lien.chemin}
                className={cn(
                  "flex flex-1 items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  estActif
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                )}
              >
                <lien.Icone className="h-5 w-5 shrink-0" />
                {sidebarOuverte && <span className="truncate" title={lien.nom}>{lien.nom}</span>}
                {sidebarOuverte && lien.chemin === "/famille" && nbRappelsDanger > 0 && (
                  <Badge variant="destructive" className="ml-auto h-5 min-w-5 px-1 text-xs flex items-center justify-center shrink-0">
                    {nbRappelsDanger}
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
                  aria-expanded={estOuverte ? "true" : "false"}
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
              {/* Sous-liens */}
              {aSousliens && estOuverte && sidebarOuverte && (
                <div className="ml-5 mt-1 space-y-0.5 border-l pl-3">
                  {lien.sousLiens!.map((sous) => {
                    const sousActif = pathname === sous.chemin;
                    return (
                      <Link
                        key={sous.chemin}
                        href={sous.chemin}
                        aria-label={sous.nom}
                        className={cn(
                          "flex items-center gap-2 rounded-md px-2 py-1.5 text-xs transition-colors",
                          sousActif
                            ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                            : "text-sidebar-foreground/60 hover:bg-sidebar-accent/40 hover:text-sidebar-accent-foreground"
                        )}
                      >
                        <sous.Icone className="h-3.5 w-3.5 shrink-0" />
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

      {/* Paramètres en bas */}
      <Separator />
      <div className="p-2 space-y-0.5">
        {estAdmin && (
          <Link
            href="/admin"
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              pathname.startsWith("/admin")
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50"
            )}
          >
            <Shield className="h-5 w-5 shrink-0" />
            {sidebarOuverte && <span>Admin</span>}
          </Link>
        )}
      </div>
    </aside>
  );
}
