// -----------------------------------------------------------
// Menu de commandes — Navigation rapide Cmd+K
// Inclut recherche API globale (B11)
// -----------------------------------------------------------

"use client";

import { useEffect, useMemo, useState, type ComponentType } from "react";
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
import { clientApi } from "@/bibliotheque/api/client";
import { Search } from "lucide-react";

type Page = PageNavigation;
const PAGES = PAGES_NAVIGATION;

interface ResultatRecherche {
  type: string;
  id: number;
  titre: string;
  description?: string;
  url: string;
  icone?: string;
}

/**
 * Menu de commandes global — Cmd+K navigation rapide + recherche API.
 * Affiche toutes les pages avec recherche intelligente et historique.
 * B11: Recherche étendue couvrant notes, jardin, contrats, documents.
 */
export function MenuCommandes() {
  const { rechercheOuverte, definirRecherche } = utiliserStoreUI();
  const [historique, setHistorique] = utiliserStockageLocal<string[]>("command-history", []);
  const [recherche, setRecherche] = useState("");
  const [resultatsAPI, setResultatsAPI] = useState<ResultatRecherche[]>([]);
  const [chargementAPI, setChargementAPI] = useState(false);
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

  // Reset on close
  useEffect(() => {
    if (!rechercheOuverte) {
      setRecherche("");
      setResultatsAPI([]);
    }
  }, [rechercheOuverte]);

  // B11: Recherche API avec debounce
  useEffect(() => {
    if (recherche.length < 3) {
      setResultatsAPI([]);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setChargementAPI(true);
      try {
        const { data } = await clientApi.get("/api/v1/recherche/global", {
          params: { q: recherche, limit: 10 },
        });
        setResultatsAPI(Array.isArray(data) ? data : []);
      } catch {
        setResultatsAPI([]);
      } finally {
        setChargementAPI(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [recherche]);

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
      <CommandInput
        placeholder="Rechercher pages, recettes, notes, contrats..."
        value={recherche}
        onValueChange={setRecherche}
      />
      <CommandList>
        <CommandEmpty>
          {chargementAPI ? "Recherche en cours..." : "Aucun résultat trouvé"}
        </CommandEmpty>

        {/* B11: Résultats API */}
        {resultatsAPI.length > 0 && (
          <>
            <CommandGroup heading="Résultats">
              {resultatsAPI.map((r) => (
                <CommandItem
                  key={`api-${r.type}-${r.id}`}
                  value={`api-${r.titre.toLowerCase()} ${r.description?.toLowerCase() || ""}`}
                  onSelect={() => handleSelect(r.url)}
                  className="flex items-center gap-2"
                >
                  <span className="text-base shrink-0">{r.icone || "??"}</span>
                  <div className="flex-1 min-w-0">
                    <span className="text-sm">{r.titre}</span>
                    {r.description && (
                      <p className="text-xs text-muted-foreground truncate">{r.description}</p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">{r.type}</span>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

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
