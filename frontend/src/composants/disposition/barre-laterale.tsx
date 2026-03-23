// ═══════════════════════════════════════════════════════════
// Barre latérale — Navigation desktop
// ═══════════════════════════════════════════════════════════

"use client";

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
} from "lucide-react";
import { cn } from "@/lib/utils";
import { utiliserStoreUI } from "@/stores/store-ui";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const ICONES: Record<string, React.ElementType> = {
  Home,
  ChefHat,
  Users,
  Calendar,
  House,
  Gamepad2,
  Wrench,
  Settings,
};

const LIENS = [
  { nom: "Accueil", chemin: "/", icone: "Home" },
  { nom: "Cuisine", chemin: "/cuisine", icone: "ChefHat" },
  { nom: "Famille", chemin: "/famille", icone: "Users" },
  { nom: "Planning", chemin: "/planning", icone: "Calendar" },
  { nom: "Maison", chemin: "/maison", icone: "House" },
  { nom: "Jeux", chemin: "/jeux", icone: "Gamepad2" },
  { nom: "Outils", chemin: "/outils", icone: "Wrench" },
] as const;

export function BarreLaterale() {
  const pathname = usePathname();
  const { sidebarOuverte, basculerSidebar } = utiliserStoreUI();

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
      <nav className="flex-1 space-y-1 p-2">
        {LIENS.map((lien) => {
          const Icone = ICONES[lien.icone];
          const estActif =
            lien.chemin === "/"
              ? pathname === "/"
              : pathname.startsWith(lien.chemin);

          const boutonContenu = (
            <Link
              href={lien.chemin}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                estActif
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
              )}
            >
              <Icone className="h-5 w-5 shrink-0" />
              {sidebarOuverte && <span className="truncate">{lien.nom}</span>}
            </Link>
          );

          // Tooltip en mode collapsed
          if (!sidebarOuverte) {
            return (
              <Tooltip key={lien.chemin}>
                <TooltipTrigger asChild>{boutonContenu}</TooltipTrigger>
                <TooltipContent side="right">{lien.nom}</TooltipContent>
              </Tooltip>
            );
          }

          return <div key={lien.chemin}>{boutonContenu}</div>;
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
