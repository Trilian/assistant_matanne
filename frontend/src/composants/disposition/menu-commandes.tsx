// ═══════════════════════════════════════════════════════════
// Menu de commandes — Navigation rapide Cmd+K
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useMemo } from "react";
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
import {
  Home,
  ChefHat,
  Users,
  House,
  Gamepad2,
  Wrench,
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
  MessageSquare,
  ArrowLeftRight,
  CloudSun,
  Timer,
  StickyNote,
  Cake,
  Contact,
  Layers,
  Shield,
  Camera,
  Apple,
  CalendarCheck,
  Wifi,
} from "lucide-react";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { utiliserStoreUI } from "@/magasins/store-ui";

interface Page {
  nom: string;
  chemin: string;
  categorie: string;
  icone: React.ElementType;
  keywords?: string[]; // Mots-clés pour recherche
}

const PAGES: Page[] = [
  // Dashboard
  { nom: "Accueil", chemin: "/", categorie: "Principal", icone: Home },

  // Cuisine
  { nom: "Cuisine", chemin: "/cuisine", categorie: "Cuisine", icone: ChefHat },
  { nom: "Recettes", chemin: "/cuisine/recettes", categorie: "Cuisine", icone: BookOpen, keywords: ["plats", "repas"] },
  { nom: "Planning Repas", chemin: "/cuisine/planning", categorie: "Cuisine", icone: CalendarDays, keywords: ["semaine", "menu"] },
  { nom: "Ma Semaine", chemin: "/cuisine/ma-semaine", categorie: "Cuisine", icone: CalendarCheck, keywords: ["planning", "hebdo"] },
  { nom: "Courses", chemin: "/cuisine/courses", categorie: "Cuisine", icone: ShoppingCart, keywords: ["achats", "liste"] },
  { nom: "Inventaire", chemin: "/cuisine/inventaire", categorie: "Cuisine", icone: Package, keywords: ["stock", "frigo"] },
  { nom: "Batch Cooking", chemin: "/cuisine/batch-cooking", categorie: "Cuisine", icone: CookingPot, keywords: ["preparation", "avance"] },
  { nom: "Anti-Gaspillage", chemin: "/cuisine/anti-gaspillage", categorie: "Cuisine", icone: Leaf, keywords: ["restes", "eco"] },
  { nom: "Photo Frigo", chemin: "/cuisine/photo-frigo", categorie: "Cuisine", icone: Camera, keywords: ["scan"] },

  // Famille
  { nom: "Famille", chemin: "/famille", categorie: "Famille", icone: Users },
  { nom: "Jules", chemin: "/famille/jules", categorie: "Famille", icone: Baby, keywords: ["enfant", "bebe", "developpement"] },
  { nom: "Activités", chemin: "/famille/activites", categorie: "Famille", icone: ClipboardList, keywords: ["sortie", "loisirs"] },
  { nom: "Routines", chemin: "/famille/routines", categorie: "Famille", icone: RotateCw, keywords: ["habitudes", "quotidien"] },
  { nom: "Budget Famille", chemin: "/famille/budget", categorie: "Famille", icone: Wallet, keywords: ["argent", "finances"] },
  { nom: "Weekend", chemin: "/famille/weekend", categorie: "Famille", icone: CalendarDays, keywords: ["sortie", "we"] },
  { nom: "Anniversaires", chemin: "/famille/anniversaires", categorie: "Famille", icone: Cake, keywords: ["fetes", "dates"] },
  { nom: "Contacts", chemin: "/famille/contacts", categorie: "Famille", icone: Contact, keywords: ["annuaire", "telephone"] },
  { nom: "Journal", chemin: "/famille/journal", categorie: "Famille", icone: BookOpen, keywords: ["memoires", "notes"] },
  { nom: "Documents", chemin: "/famille/documents", categorie: "Famille", icone: FileText, keywords: ["fichiers", "papiers"] },

  // Maison - Gestion & Entretien
  { nom: "Maison", chemin: "/maison", categorie: "Maison", icone: House },
  { nom: "Projets Maison", chemin: "/maison/projets", categorie: "Maison - Gestion", icone: Hammer, keywords: ["travaux", "renovation"] },
  { nom: "Ménage", chemin: "/maison/menage", categorie: "Maison - Entretien", icone: SprayCan, keywords: ["nettoyage", "proprete"] },
  { nom: "Jardin", chemin: "/maison/jardin", categorie: "Maison - Jardin", icone: Sprout, keywords: ["plantes", "potager"] },
  { nom: "Entretien", chemin: "/maison/entretien", categorie: "Maison - Entretien", icone: SprayCan, keywords: ["maintenance", "reparation"] },
  { nom: "Domotique", chemin: "/maison/domotique", categorie: "Maison - Tech", icone: Wifi, keywords: ["smart", "connecte"] },

  // Maison - Finances
  { nom: "Charges", chemin: "/maison/charges", categorie: "Maison - Finances", icone: Receipt, keywords: ["factures", "mensuel"] },
  { nom: "Dépenses", chemin: "/maison/depenses", categorie: "Maison - Finances", icone: Banknote, keywords: ["budget", "argent"] },
  { nom: "Énergie", chemin: "/maison/energie", categorie: "Maison - Finances", icone: Zap, keywords: ["electricite", "consommation"] },

  // Maison - Stocks & Inventaire
  { nom: "Stocks", chemin: "/maison/stocks", categorie: "Maison - Stocks", icone: Package, keywords: ["reserve", "cave"] },
  { nom: "Cellier", chemin: "/maison/cellier", categorie: "Maison - Stocks", icone: Wine, keywords: ["vin", "bouteilles"] },

  // Maison - Admin
  { nom: "Artisans", chemin: "/maison/artisans", categorie: "Maison - Admin", icone: Wrench, keywords: ["contacts", "pro"] },
  { nom: "Contrats", chemin: "/maison/contrats", categorie: "Maison - Admin", icone: FileText, keywords: ["assurance", "abonnement"] },
  { nom: "Garanties", chemin: "/maison/garanties", categorie: "Maison - Admin", icone: ShieldCheck, keywords: ["sav", "protection"] },
  { nom: "Diagnostics", chemin: "/maison/diagnostics", categorie: "Maison - Admin", icone: ClipboardCheck, keywords: ["dpe", "controle"] },

  // Maison - Visualisation
  { nom: "Visualisation Maison", chemin: "/maison/visualisation", categorie: "Maison - Vue", icone: Layers, keywords: ["plan", "vue"] },
  { nom: "Éco-Tips", chemin: "/maison/eco-tips", categorie: "Maison - Écologie", icone: Leaf, keywords: ["economie", "energie"] },

  // Jeux
  { nom: "Jeux", chemin: "/jeux", categorie: "Jeux", icone: Gamepad2 },
  { nom: "Paris Sportifs", chemin: "/jeux/paris", categorie: "Jeux", icone: Trophy, keywords: ["pari", "sport"] },
  { nom: "Loto", chemin: "/jeux/loto", categorie: "Jeux", icone: Dices, keywords: ["tirage", "fdj"] },
  { nom: "EuroMillions", chemin: "/jeux/euromillions", categorie: "Jeux", icone: Dices, keywords: ["euro", "tirage"] },
  { nom: "Performance Jeux", chemin: "/jeux/performance", categorie: "Jeux", icone: TrendingUp, keywords: ["stats", "resultats"] },
  { nom: "Jeu Responsable", chemin: "/jeux/responsable", categorie: "Jeux", icone: Shield, keywords: ["limites", "controle"] },

  // Outils
  { nom: "Outils", chemin: "/outils", categorie: "Outils", icone: Wrench },
  { nom: "Chat IA", chemin: "/outils/chat-ia", categorie: "Outils", icone: MessageSquare, keywords: ["assistant", "question"] },
  { nom: "Convertisseur", chemin: "/outils/convertisseur", categorie: "Outils", icone: ArrowLeftRight, keywords: ["unite", "mesure"] },
  { nom: "Météo", chemin: "/outils/meteo", categorie: "Outils", icone: CloudSun, keywords: ["previsions", "temps"] },
  { nom: "Minuteur", chemin: "/outils/minuteur", categorie: "Outils", icone: Timer, keywords: ["chrono", "cuisson"] },
  { nom: "Notes", chemin: "/outils/notes", categorie: "Outils", icone: StickyNote, keywords: ["memo", "pense-bete"] },
  { nom: "Nutritionniste", chemin: "/outils/nutritionniste", categorie: "Outils", icone: Apple, keywords: ["sante", "calories"] },
];

/**
 * Menu de commandes global — Cmd+K navigation rapide.
 * Affiche toutes les pages avec recherche intelligente et historique.
 */
export function MenuCommandes() {
  const { rechercheOuverte, definirRecherche } = utiliserStoreUI();
  const [historique, setHistorique] = utiliserStockageLocal<string[]>("command-history", []);
  const router = useRouter();

  // Cmd+K / Ctrl+K (le raccourci est aussi géré dans le header)
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
    // Ajouter à l'historique (max 10)
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

  // Pages récentes depuis historique
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
                const Icone = page.icone;
                return (
                  <CommandItem
                    key={page.chemin}
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

        {/* Toutes les pages groupées */}
        {groupes.map(([categorie, pages]) => (
          <CommandGroup key={categorie} heading={categorie}>
            {pages.map((page) => {
              const Icone = page.icone;
              const searchValue = [
                page.nom,
                page.categorie,
                ...(page.keywords || []),
              ].join(" ").toLowerCase();

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
