// -----------------------------------------------------------
// Menu de commandes — Navigation rapide Cmd+K
// Inclut recherche API globale (B11)
// -----------------------------------------------------------

"use client";

import { useEffect, useMemo, useState, type ComponentType } from "react";
import { useRouter } from "next/navigation";
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/composants/ui/command";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { PAGES_NAVIGATION, type PageNavigation } from "@/bibliotheque/pages-navigation";
import { clientApi } from "@/bibliotheque/api/client";
import { creerListeCourses, ajouterArticle } from "@/bibliotheque/api/courses";
import { creerNote } from "@/bibliotheque/api/outils";
import { creerRecette } from "@/bibliotheque/api/recettes";
import { creerScenarioHabitat } from "@/bibliotheque/api/habitat";
import { resetOnboarding } from "@/composants/disposition/tour-onboarding";
import { toast } from "sonner";
import {
  Wand2,
  TimerReset,
  StickyNote,
  ShoppingCart,
  Home,
  Sparkles,
  ChefHat,
  CalendarPlus,
  Wrench,
  Users,
} from "lucide-react";

type Page = PageNavigation;
const PAGES = PAGES_NAVIGATION;

interface ResultatRecherche {
  type: string;
  id: number;
  titre: string;
  description?: string;
  url: string;
  icone?: string;
  categorie?: string;
  statut?: string;
}

interface ActionUniverselle {
  id: string;
  titre: string;
  description: string;
  raccourci?: string;
  motCle: string;
  icone: ComponentType<{ className?: string }>;
  executer: () => Promise<void> | void;
}

function normaliser(texte: string): string {
  return texte
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
}

function extraireNomArticle(recherche: string): string | null {
  const match = recherche.match(/ajout(?:e|er)?\s+(.+?)\s+(?:a|à)\s+la\s+liste/i);
  if (!match?.[1]) {
    return null;
  }
  return match[1].trim();
}

function extraireDureeMinuteur(recherche: string): number | null {
  const match = recherche.match(/minuteur\s+(\d{1,3})/i);
  if (!match?.[1]) {
    return null;
  }
  const valeur = Number(match[1]);
  return Number.isFinite(valeur) && valeur > 0 ? valeur : null;
}

function extraireNomRecette(recherche: string): string | null {
  const match = recherche.match(/recette\s+(.{3,80})/i);
  return match?.[1]?.trim() ?? null;
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
  const [actionEnCours, setActionEnCours] = useState<string | null>(null);
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

  const executerAction = async (action: ActionUniverselle) => {
    definirRecherche(false);
    setActionEnCours(action.id);
    try {
      await action.executer();
    } catch {
      toast.error("Impossible d'exécuter cette action rapide");
    } finally {
      setActionEnCours(null);
    }
  };

  const actionsUniverselles = useMemo<ActionUniverselle[]>(() => {
    const terme = recherche.trim();
    const articleRapide = extraireNomArticle(terme);
    const dureeMinuteur = extraireDureeMinuteur(terme);
    const nomRecette = extraireNomRecette(terme);

    const actions: ActionUniverselle[] = [
      {
        id: "recette-rapide",
        titre: "Ajouter une recette rapide",
        description: "Crée une nouvelle recette et ouvre sa fiche pour compléter.",
        raccourci: "R",
        motCle: "recette recipe ajouter creer nouvelle plat cuisine",
        icone: ChefHat,
        executer: async () => {
          const nom = terme.length >= 3 ? terme.slice(0, 120) : "Nouvelle recette";
          const recette = await creerRecette({ nom, description: "", ingredients: [] });
          toast.success(`Recette créée: ${recette.nom}`);
          router.push(`/cuisine/recettes/${recette.id}`);
        },
      },
      {
        id: "planifier-semaine",
        titre: "Planifier ma semaine repas",
        description: "Lance la génération IA du planning de la semaine.",
        raccourci: "P",
        motCle: "planifier semaine planning repas generer menu",
        icone: CalendarPlus,
        executer: () => {
          router.push("/cuisine/planning?action=generer");
          toast.success("Ouverture du planning...");
        },
      },
      {
        id: "tache-maison",
        titre: "Ajouter une tâche maison",
        description: "Ouvre l'entretien pour créer une nouvelle tâche.",
        motCle: "tache maison entretien reparation bricolage travaux",
        icone: Wrench,
        executer: () => {
          router.push("/maison/entretien?nouvelle=true");
          toast.success("Ouverture de l'entretien...");
        },
      },
      {
        id: "activite-famille",
        titre: "Ajouter une activité famille",
        description: "Ouvre les activités pour planifier une nouvelle sortie.",
        motCle: "activite famille sortie loisir weekend jules",
        icone: Users,
        executer: () => {
          router.push("/famille/activites?nouvelle=true");
          toast.success("Ouverture des activités...");
        },
      },
      {
        id: "courses-nouvelle-liste",
        titre: "Créer une nouvelle liste de courses",
        description: "Ajoute immédiatement une liste active dans Cuisine > Courses.",
        raccourci: "N",
        motCle: "nouvelle liste courses shopping panier",
        icone: ShoppingCart,
        executer: async () => {
          const liste = await creerListeCourses("Liste rapide");
          toast.success(`Liste créée: ${liste.nom}`);
          router.push(`/cuisine/courses?liste=${liste.id}`);
        },
      },
      {
        id: "note-rapide",
        titre: "Créer une note rapide",
        description: "Ouvre les notes avec un brouillon prêt à compléter.",
        raccourci: "N",
        motCle: "note memo brouillon rapide",
        icone: StickyNote,
        executer: async () => {
          const titre = terme.length >= 3 ? terme.slice(0, 80) : "Note rapide";
          const note = await creerNote({ titre, contenu: terme.length >= 3 ? terme : undefined, categorie: "general" });
          toast.success(`Note créée: ${note.titre}`);
          router.push("/outils/notes");
        },
      },
      {
        id: "scenario-habitat",
        titre: "Créer un scénario Habitat brouillon",
        description: "Ajoute un scénario brouillon pour arbitrer un projet logement.",
        motCle: "scenario habitat maison logement brouillon",
        icone: Home,
        executer: async () => {
          const scenario = await creerScenarioHabitat({
            nom: terme.length >= 3 ? terme.slice(0, 120) : "Nouveau scénario",
            description: terme.length >= 3 ? terme : "Créé depuis la palette de commandes",
            statut: "brouillon",
          });
          toast.success(`Scénario créé: ${scenario.nom}`);
          router.push("/vision-maison/scenarios");
        },
      },
      {
        id: "onboarding",
        titre: "Rejouer l'onboarding guidé",
        description: "Réinitialise le tour utilisateur pour revoir les 5 étapes clés.",
        motCle: "onboarding tour guide decouverte replay",
        icone: Sparkles,
        executer: () => {
          resetOnboarding();
          router.refresh();
          toast.success("Le tour d'onboarding sera réaffiché");
        },
      },
    ];

    if (articleRapide) {
      actions.unshift({
        id: "ajout-article-rapide",
        titre: `Ajouter \"${articleRapide}\" à une liste de courses`,
        description: "Crée d'abord une liste rapide, puis y ajoute l'article demandé.",
        motCle: `ajoute ${articleRapide} a la liste courses rapide`,
        icone: Wand2,
        executer: async () => {
          const liste = await creerListeCourses("Liste rapide");
          await ajouterArticle(liste.id, { nom: articleRapide });
          toast.success(`${articleRapide} ajouté à ${liste.nom}`);
          router.push(`/cuisine/courses?liste=${liste.id}`);
        },
      });
    }

    if (dureeMinuteur) {
      actions.unshift({
        id: `minuteur-${dureeMinuteur}`,
        titre: `Lancer un minuteur de ${dureeMinuteur} min`,
        description: "Ouvre la page minuteur avec une durée préremplie.",
        motCle: `minuteur ${dureeMinuteur} cuisson timer`,
        icone: TimerReset,
        executer: () => {
          router.push(`/outils/minuteur?minutes=${dureeMinuteur}`);
        },
      });
    }

    if (nomRecette) {
      actions.unshift({
        id: "recette-nommee",
        titre: `Créer la recette \"${nomRecette}\"`,
        description: "Crée directement une recette avec ce nom.",
        motCle: `recette ${nomRecette} creer ajouter`,
        icone: ChefHat,
        executer: async () => {
          const recette = await creerRecette({ nom: nomRecette, description: "", ingredients: [] });
          toast.success(`Recette créée: ${recette.nom}`);
          router.push(`/cuisine/recettes/${recette.id}`);
        },
      });
    }

    return actions;
  }, [recherche, router]);

  const actionsFiltrees = useMemo(() => {
    const terme = normaliser(recherche);
    if (!terme) {
      return actionsUniverselles;
    }

    return actionsUniverselles.filter((action) => {
      const corpus = normaliser(`${action.titre} ${action.description} ${action.motCle}`);
      return corpus.includes(terme);
    });
  }, [actionsUniverselles, recherche]);

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
      <Command>
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
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{r.titre}</span>
                      <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-muted-foreground">
                        {r.type}
                      </span>
                    </div>
                    {r.description && (
                      <p className="text-xs text-muted-foreground truncate">{r.description}</p>
                    )}
                    {(r.categorie || r.statut) && (
                      <p className="text-[11px] text-muted-foreground truncate">
                        {[r.categorie, r.statut].filter(Boolean).join(" · ")}
                      </p>
                    )}
                  </div>
                  <CommandShortcut>Entrée</CommandShortcut>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {actionsFiltrees.length > 0 && (
          <>
            <CommandGroup heading="Actions rapides">
              {actionsFiltrees.map((action) => {
                const Icone = action.icone;
                return (
                  <CommandItem
                    key={action.id}
                    value={`action-${action.titre.toLowerCase()} ${action.motCle}`}
                    onSelect={() => void executerAction(action)}
                    className="flex items-center gap-2"
                    disabled={actionEnCours === action.id}
                  >
                    <Icone className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <span className="text-sm font-medium">{action.titre}</span>
                      <p className="text-xs text-muted-foreground truncate">{action.description}</p>
                    </div>
                    {action.raccourci ? <CommandShortcut>{action.raccourci}</CommandShortcut> : null}
                  </CommandItem>
                );
              })}
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
      </Command>
    </CommandDialog>
  );
}
