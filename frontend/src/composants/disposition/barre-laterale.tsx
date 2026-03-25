// ═══════════════════════════════════════════════════════════
// Barre latérale — Navigation desktop avec sous-menus
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  ChefHat,
  Users,
  Calendar,
  House,
  Gamepad2,
  Wrench,
  Settings,
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
  MessageSquare,
  ArrowLeftRight,
  CloudSun,
  Timer,
  StickyNote,
  Cake,
  Contact,
  Layers,
} from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { Button } from "@/composants/ui/button";
import { Separator } from "@/composants/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/composants/ui/tooltip";

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
      { nom: "Weekend", chemin: "/famille/weekend", Icone: Calendar },
      { nom: "Anniversaires", chemin: "/famille/anniversaires", Icone: Cake },
      { nom: "Contacts", chemin: "/famille/contacts", Icone: Contact },
      { nom: "Journal", chemin: "/famille/journal", Icone: BookOpen },
      { nom: "Documents", chemin: "/famille/documents", Icone: FileText },
    ],
  },
  { nom: "Planning", chemin: "/planning", Icone: Calendar },
  {
    nom: "Maison",
    chemin: "/maison",
    Icone: House,
    sousLiens: [
      { nom: "Projets", chemin: "/maison/projets", Icone: Hammer },
      { nom: "Jardin", chemin: "/maison/jardin", Icone: Sprout },
      { nom: "Entretien", chemin: "/maison/entretien", Icone: SprayCan },
      { nom: "Charges", chemin: "/maison/charges", Icone: Receipt },
      { nom: "Dépenses", chemin: "/maison/depenses", Icone: Banknote },
      { nom: "Énergie", chemin: "/maison/energie", Icone: Zap },
      { nom: "Stocks", chemin: "/maison/stocks", Icone: Package },
      { nom: "Cellier", chemin: "/maison/cellier", Icone: Wine },
      { nom: "Artisans", chemin: "/maison/artisans", Icone: Wrench },
      { nom: "Contrats", chemin: "/maison/contrats", Icone: FileText },
      { nom: "Garanties", chemin: "/maison/garanties", Icone: ShieldCheck },
      { nom: "Diagnostics", chemin: "/maison/diagnostics", Icone: ClipboardCheck },
      { nom: "Visualisation", chemin: "/maison/visualisation", Icone: Layers },
      { nom: "Éco-Tips", chemin: "/maison/eco-tips", Icone: Leaf },
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
    ],
  },
  {
    nom: "Outils",
    chemin: "/outils",
    Icone: Wrench,
    sousLiens: [
      { nom: "Chat IA", chemin: "/outils/chat-ia", Icone: MessageSquare },
      { nom: "Convertisseur", chemin: "/outils/convertisseur", Icone: ArrowLeftRight },
      { nom: "Météo", chemin: "/outils/meteo", Icone: CloudSun },
      { nom: "Minuteur", chemin: "/outils/minuteur", Icone: Timer },
      { nom: "Notes", chemin: "/outils/notes", Icone: StickyNote },
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
  const [sectionsOuvertes, setSectionsOuvertes] = useState<Set<string>>(() => {
    // Ouvrir automatiquement la section active
    const initial = new Set<string>();
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
      return next;
    });
  };

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300",
        sidebarOuverte ? "w-56" : "w-16"
      )}
    >
      {/* Logo / Titre */}
      <div className="flex h-14 items-center gap-2 border-b px-4">
        <span className="text-lg">🏠</span>
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
        >
          {sidebarOuverte ? (
            <PanelLeftClose className="h-4 w-4" />
          ) : (
            <PanelLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto space-y-1 p-2">
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
                {sidebarOuverte && <span className="truncate">{lien.nom}</span>}
              </Link>
              {sidebarOuverte && aSousliens && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    basculerSection(lien.chemin);
                  }}
                  className="p-1 rounded hover:bg-sidebar-accent/50 text-sidebar-foreground/50"
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
      <div className="p-2">
        <Link
          href="/parametres"
          className={cn(
            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
            pathname === "/parametres"
              ? "bg-sidebar-accent text-sidebar-accent-foreground"
              : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50"
          )}
        >
          <Settings className="h-5 w-5 shrink-0" />
          {sidebarOuverte && <span>Paramètres</span>}
        </Link>
      </div>
    </aside>
  );
}
