// ═══════════════════════════════════════════════════════════
// En-tête — Barre supérieure avec recherche + profil
// ═══════════════════════════════════════════════════════════

"use client";

import { Search, Moon, Sun, LogOut, User, BookOpen } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/composants/ui/button";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/composants/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/composants/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/composants/ui/tooltip";

/**
 * Barre supérieure de l'application — recherche globale, bascule de thème, menu profil.
 */
export function EnTete() {
  const { theme, setTheme } = useTheme();
  const { basculerRecherche } = utiliserStoreUI();
  const { utilisateur, deconnecter } = utiliserAuth();

  const initialesUtilisateur = utilisateur?.nom
    ? utilisateur.nom
        .split(" ")
        .map((m) => m[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "?";

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background px-4 md:px-6">
      {/* Titre mobile */}
      <span className="text-lg font-semibold md:hidden">🏠 Matanne</span>

      {/* Barre de recherche */}
      <Button
        variant="outline"
        className="ml-auto hidden md:flex items-center gap-2 text-muted-foreground"
        onClick={basculerRecherche}
      >
        <Search className="h-4 w-4" />
        <span className="text-sm">Rechercher...</span>
        <kbd className="pointer-events-none ml-4 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-xs font-medium text-muted-foreground sm:flex">
          ⌘K
        </kbd>
      </Button>

      {/* Bouton recherche mobile */}
      <Button
        variant="ghost"
        size="icon"
        className="ml-auto md:hidden"
        onClick={basculerRecherche}
        aria-label="Rechercher"
      >
        <Search className="h-5 w-5" />
      </Button>

      {/* Lien vers guide utilisateur */}
      <Button
        variant="ghost"
        size="icon"
        asChild
        title="Guide utilisateur"
      >
        <a href="https://github.com/votreorg/assistant-matanne/blob/main/docs/user-guide/README.md" target="_blank" rel="noopener noreferrer">
          <BookOpen className="h-5 w-5" />
          <span className="sr-only">Guide utilisateur</span>
        </a>
      </Button>

      {/* Toggle thème */}
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Changer le thème</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Changer le thème (Clair/Sombre)</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      {/* Menu profil */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="rounded-full" aria-label="Mon profil">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="text-xs">
                {initialesUtilisateur}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48">
          <div className="px-2 py-1.5">
            <p className="text-sm font-medium">{utilisateur?.nom ?? "Utilisateur"}</p>
            <p className="text-xs text-muted-foreground">{utilisateur?.email}</p>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <a href="/parametres" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Paramètres
            </a>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            className="flex items-center gap-2 text-destructive"
            onClick={deconnecter}
          >
            <LogOut className="h-4 w-4" />
            Déconnexion
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
