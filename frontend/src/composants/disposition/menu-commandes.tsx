// ═══════════════════════════════════════════════════════════
// Menu de commandes — Navigation rapide Cmd+K
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useMemo, type ComponentType } from "react";
import { useRouter } from "next/navigation";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/composants/ui/command";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { PAGES_NAVIGATION, type PageNavigation } from "@/bibliotheque/pages-navigation";

type Page = PageNavigation;
const PAGES = PAGES_NAVIGATION;

/**
 * Menu de commandes global — Cmd+K navigation rapide.
 * Affiche toutes les pages avec recherche intelligente et historique.
 * La liste des pages est importée depuis la source unique `pages-navigation.ts`.
 */
export function MenuCommandes() {
  const { rechercheOuverte, definirRecherche } = utiliserStoreUI();
  const [historique, setHistorique] = utiliserStockageLocal<string[]>("command-history", []);
  const router = useRouter();

  // Cmd+K / Ctrl+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        definirRecherche(!rechercheOuverte);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [rechercheOuverte, definirRecherche]);

  const handleSelect = (chemin: string) => {
    setHistorique((prev) => {
      const next = [chemin, ...prev.filter((p) => p !== chemin)];
      return next.slice(0, 10);
    });
    definirRecherche(false);
    router.push(chemin);
  };

  // Grouper par catégorie
  const groupes = useMemo(() => {
    const map = new Map<string, Page[]>();
    for (const page of PAGES) {
      const current = map.get(page.categorie) || [];
      current.push(page);
      map.set(page.categorie, current);
    }
    return Array.from(map.entries());
  }, []);

  // Pages récentes depuis historique (max 5)
  const pagesRecentes = useMemo(() => {
    return historique
      .map((chemin) => PAGES.find((p) => p.chemin === chemin))
      .filter((p): p is Page => p !== undefined)
      .slice(0, 5);
  }, [historique]);

  return (
    <CommandDialog open={rechercheOuverte} onOpenChange={definirRecherche}>
      <CommandInput placeholder="Rechercher une page..." />
      <CommandList>
        <CommandEmpty>Aucune page trouvée</CommandEmpty>

        {/* Récents */}
        {pagesRecentes.length > 0 && (
          <>
            <CommandGroup heading="Récents">
              {pagesRecentes.map((page) => {
                const Icone = page.Icone as ComponentType<{ className?: string }>;
                return (
                  <CommandItem
                    key={`recent-${page.chemin}`}
                    value={`recent-${page.nom.toLowerCase()}`}
                    onSelect={() => handleSelect(page.chemin)}
                    className="flex items-center gap-2"
                  >
                    <Icone className="h-4 w-4 text-muted-foreground" />
                    <span>{page.nom}</span>
                  </CommandItem>
                );
              })}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {/* Toutes les pages groupées par catégorie */}
        {groupes.map(([categorie, pages]) => (
          <CommandGroup key={categorie} heading={categorie}>
            {pages.map((page) => {
              const Icone = page.Icone as ComponentType<{ className?: string }>;
              const searchValue = [
                page.nom,
                page.categorie,
                ...(page.keywords || []),
              ]
                .join(" ")
                .toLowerCase();

              return (
                <CommandItem
                  key={page.chemin}
                  value={searchValue}
                  onSelect={() => handleSelect(page.chemin)}
                  className="flex items-center gap-2"
                >
                  <Icone className="h-4 w-4 text-muted-foreground" />
                  <span>{page.nom}</span>
                </CommandItem>
              );
            })}
          </CommandGroup>
        ))}
      </CommandList>
    </CommandDialog>
  );
}
