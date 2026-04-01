// ═══════════════════════════════════════════════════════════
// Planning Repas — Grille hebdomadaire unifiée
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo, useCallback } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Plus,
  X,
  Loader2,
  Download,
  Search,
  Clock,
  ShoppingCart,
  CookingPot,
  CalendarDays,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { Badge } from "@/composants/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/composants/ui/tabs";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  obtenirPlanningSemaine,
  obtenirPlanningMensuel,
  obtenirConflitsPlanning,
  definirRepas,
  supprimerRepas,
  genererPlanningSemaine,
  exporterPlanningIcal,
  exporterPlanningPdf,
  obtenirNutritionHebdo,
  obtenirSuggestionsRapides,
} from "@/bibliotheque/api/planning";
import { toast } from "sonner";
import { genererCoursesDepuisPlanning, type GenererCoursesResult } from "@/bibliotheque/api/courses";
import { genererSessionDepuisPlanning } from "@/bibliotheque/api/batch-cooking";
import type { GenererSessionDepuisPlanningResult } from "@/types/batch-cooking";
import type {
  TypeRepas,
  RepasPlanning,
  CreerRepasPlanningDTO,
  SuggestionRecettePlanning,
} from "@/types/planning";
import { BadgeNutriscore } from "@/composants/cuisine/badge-nutriscore";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { ConvertisseurInline } from "@/composants/cuisine/convertisseur-inline";
import { CalendrierMensuel } from "@/composants/planning/calendrier-mensuel";
import { utiliserModeInvites } from "@/crochets/utiliser-mode-invites";
import { listerEvenementsFamiliaux } from "@/bibliotheque/api/famille";
import { listerEvenements } from "@/bibliotheque/api/calendriers";

const JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
const TYPES_REPAS: { valeur: TypeRepas; label: string; emoji: string }[] = [
  { valeur: "petit_dejeuner", label: "Petit-déj", emoji: "🌅" },
  { valeur: "dejeuner", label: "Déjeuner", emoji: "☀️" },
  { valeur: "gouter", label: "Goûter", emoji: "🍪" },
  { valeur: "diner", label: "Dîner", emoji: "🌙" },
];

function getLundiDeSemaine(offset: number): string {
  const now = new Date();
  const jour = now.getDay();
  const diff = jour === 0 ? -6 : 1 - jour;
  const lundi = new Date(now);
  lundi.setDate(now.getDate() + diff + offset * 7);
  return lundi.toISOString().split("T")[0];
}

function getDatesDeSemaine(dateDebut: string): string[] {
  const dates: string[] = [];
  const lundi = new Date(dateDebut);
  for (let i = 0; i < 7; i++) {
    const d = new Date(lundi);
    d.setDate(lundi.getDate() + i);
    dates.push(d.toISOString().split("T")[0]);
  }
  return dates;
}

export default function PagePlanning() {
  const { contexte: modeInvites, mettreAJour: mettreAJourModeInvites, reinitialiser: reinitialiserModeInvites } = utiliserModeInvites();
  const [modeAffichage, setModeAffichage] = useState<"semaine" | "mois">("semaine");
  const [offsetSemaine, setOffsetSemaine] = useState(0);
  const [offsetMois, setOffsetMois] = useState(0);
  const [dialogueOuvert, setDialogueOuvert] = useState(false);
  const [repasEnCours, setRepasEnCours] = useState<{
    date: string;
    type_repas: TypeRepas;
  } | null>(null);
  const [notesRepas, setNotesRepas] = useState("");
  const [ongletDialogue, setOngletDialogue] = useState<"suggestions" | "libre">("suggestions");
  const [rechercheRecette, setRechercheRecette] = useState("");
  const [coursesDialogue, setCoursesDialogue] = useState(false);
  const [coursesResultat, setCoursesResultat] = useState<GenererCoursesResult | null>(null);
  const [batchDialogue, setBatchDialogue] = useState(false);
  const [batchResultat, setBatchResultat] = useState<GenererSessionDepuisPlanningResult | null>(null);
  const [choixModePrepa, setChoixModePrepa] = useState(false);
  const [repasGlisse, setRepasGlisse] = useState<RepasPlanning | null>(null);

  const invalider = utiliserInvalidation();
  const dateDebut = getLundiDeSemaine(offsetSemaine);
  const datesSemaine = getDatesDeSemaine(dateDebut);
  const moisDate = new Date();
  moisDate.setMonth(moisDate.getMonth() + offsetMois);
  const moisSelectionne = `${moisDate.getFullYear()}-${String(moisDate.getMonth() + 1).padStart(2, "0")}`;

  // ─── Requêtes ───
  const { data: planning, isLoading } = utiliserRequete(
    ["planning", dateDebut],
    () => obtenirPlanningSemaine(dateDebut)
  );

  const { data: planningMensuel, isLoading: chargementMensuel } = utiliserRequete(
    ["planning", "mensuel", moisSelectionne],
    () => obtenirPlanningMensuel(moisSelectionne),
    { enabled: modeAffichage === "mois" }
  );

  const { data: conflits } = utiliserRequete(
    ["planning", "conflits", dateDebut],
    () => obtenirConflitsPlanning(dateDebut),
    { staleTime: 3 * 60 * 1000 }
  );

  const { data: nutrition } = utiliserRequete(
    ["planning", "nutrition", dateDebut],
    () => obtenirNutritionHebdo(dateDebut)
  );

  const { data: suggestions, isLoading: chargeSuggestions } = utiliserRequete(
    ["planning", "suggestions", repasEnCours?.type_repas ?? "diner"],
    () => obtenirSuggestionsRapides(repasEnCours?.type_repas ?? "diner", 8),
    { enabled: dialogueOuvert }
  );

  const { data: evenementsFamille } = utiliserRequete(
    ["famille", "evenements", "planning-invites"],
    listerEvenementsFamiliaux,
    { staleTime: 10 * 60 * 1000 }
  );

  const { data: evenementsCalendrier } = utiliserRequete(
    ["calendriers", "evenements", "planning-invites"],
    () => {
      const debut = new Date().toISOString().slice(0, 10);
      const fin = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        .toISOString()
        .slice(0, 10);
      return listerEvenements({ date_debut: debut, date_fin: fin });
    },
    { staleTime: 10 * 60 * 1000 }
  );

  const contexteInvitesActif = modeInvites.actif && modeInvites.nbInvites > 0;
  const evenementsModeInvites = useMemo(() => {
    const items = [...modeInvites.evenements];
    if (modeInvites.occasion.trim()) {
      items.unshift(modeInvites.occasion.trim());
    }
    return Array.from(new Set(items.filter(Boolean))).slice(0, 6);
  }, [modeInvites.evenements, modeInvites.occasion]);

  const suggestionsInvites = useMemo(() => {
    const libellesFamille = (evenementsFamille ?? []).map((item) => item.titre).filter(Boolean);
    const libellesCalendrier = (evenementsCalendrier ?? []).map((item) => item.titre).filter(Boolean);
    return Array.from(new Set([...libellesFamille, ...libellesCalendrier])).slice(0, 6);
  }, [evenementsCalendrier, evenementsFamille]);

  // ─── Mutations ───
  const { mutate: ajouterRepas, isPending: enAjout } = utiliserMutation(
    (dto: CreerRepasPlanningDTO) => definirRepas(dto),
    {
      onSuccess: () => {
        invalider(["planning"]);
        setDialogueOuvert(false);
        setNotesRepas("");
        toast.success("Repas ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: retirerRepas } = utiliserMutation(supprimerRepas, {
    onSuccess: () => {
      invalider(["planning"]);
      toast.success("Repas retiré");
    },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  const { mutate: genererIA, isPending: enGeneration } = utiliserMutation(
    () =>
      genererPlanningSemaine({
        date_debut: dateDebut,
        nb_personnes: 4 + (contexteInvitesActif ? modeInvites.nbInvites : 0),
        preferences:
          contexteInvitesActif || evenementsModeInvites.length > 0
            ? {
                mode_invites: contexteInvitesActif,
                nb_invites: contexteInvitesActif ? modeInvites.nbInvites : 0,
                occasion: modeInvites.occasion || undefined,
                evenements: evenementsModeInvites,
              }
            : undefined,
      }),
    {
      onSuccess: () => {
        invalider(["planning"]);
        toast.success("Planning généré par l'IA !");
      },
      onError: () => toast.error("Erreur lors de la génération IA"),
    }
  );

  const { mutate: genererCourses, isPending: enGenerationCourses } = utiliserMutation(
    () =>
      genererCoursesDepuisPlanning(dateDebut, {
        nbInvites: contexteInvitesActif ? modeInvites.nbInvites : 0,
        evenements: evenementsModeInvites,
        nomListe:
          contexteInvitesActif && modeInvites.occasion
            ? `Courses ${modeInvites.occasion}`
            : undefined,
      }),
    {
      onSuccess: (result) => {
        setCoursesResultat(result);
        setCoursesDialogue(true);
        toast.success(`${result.total_articles} articles ajoutés !`);
      },
      onError: () => toast.error("Erreur lors de la génération des courses"),
    }
  );

  const { mutate: genererBatch, isPending: enGenerationBatch } = utiliserMutation(
    () => {
      if (!planning) throw new Error("Pas de planning");
      if (!planning.planning_id) {
        throw new Error("Planning sans identifiant. Générez d'abord un planning persistant.");
      }
      // Date session = dimanche de cette semaine
      const dimanche = new Date(dateDebut);
      dimanche.setDate(dimanche.getDate() + 6);
      return genererSessionDepuisPlanning({
        planning_id: planning.planning_id,
        date_session: dimanche.toISOString().split("T")[0],
      });
    },
    {
      onSuccess: (result) => {
        setBatchResultat(result);
        setBatchDialogue(true);
        toast.success(`Session batch créée avec ${result.nb_recettes} recettes !`);
      },
      onError: () => toast.error("Erreur lors de la création de la session batch"),
    }
  );

  // ─── Helpers ───
  const repasParJour = useMemo(() => {
    const map: Record<string, RepasPlanning[]> = {};
    if (planning?.repas) {
      for (const r of planning.repas) {
        const key = (r.date_repas || r.date || "").split("T")[0];
        if (!map[key]) map[key] = [];
        map[key].push(r);
      }
    }
    return map;
  }, [planning]);

  function trouverRepas(date: string, type: TypeRepas): RepasPlanning | undefined {
    return repasParJour[date]?.find((r) => r.type_repas === type);
  }

  function ouvrirDialogue(date: string, type: TypeRepas) {
    setRepasEnCours({ date, type_repas: type });
    setNotesRepas("");
    setRechercheRecette("");
    setOngletDialogue("suggestions");
    setDialogueOuvert(true);
  }

  const deplacerRepas = useCallback(
    async (dateCible: string, typeCible: TypeRepas) => {
      if (!repasGlisse) return;

      const dateSource = (repasGlisse.date_repas || repasGlisse.date || "").split("T")[0];
      if (dateSource === dateCible && repasGlisse.type_repas === typeCible) {
        setRepasGlisse(null);
        return;
      }

      try {
        await definirRepas({
          date: dateCible,
          type_repas: typeCible,
          recette_id: repasGlisse.recette_id,
          notes: repasGlisse.notes ?? repasGlisse.recette_nom,
          portions: repasGlisse.portions,
        });

        await supprimerRepas(repasGlisse.id);
        invalider(["planning"]);
        toast.success("Repas déplacé");
      } catch {
        toast.error("Impossible de déplacer ce repas");
      } finally {
        setRepasGlisse(null);
      }
    },
    [repasGlisse, invalider]
  );

  const choisirRecette = useCallback(
    (recette: SuggestionRecettePlanning) => {
      if (!repasEnCours) return;
      ajouterRepas({
        date: repasEnCours.date,
        type_repas: repasEnCours.type_repas,
        recette_id: recette.id,
        notes: recette.nom,
      });
    },
    [repasEnCours, ajouterRepas]
  );

  const suggestionsFiltrees = useMemo(() => {
    if (!suggestions) return [];
    if (!rechercheRecette.trim()) return suggestions;
    const q = rechercheRecette.toLowerCase();
    return suggestions.filter(
      (s) =>
        s.nom.toLowerCase().includes(q) ||
        (s.categorie ?? "").toLowerCase().includes(q)
    );
  }, [suggestions, rechercheRecette]);

  const moisLabel = new Date(dateDebut).toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  const moisLabelComplet = moisDate.toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="space-y-6">
      {/* ─── En-tête ─── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📅 Planning repas</h1>
          <p className="text-muted-foreground capitalize">
            {modeAffichage === "semaine" ? moisLabel : moisLabelComplet}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className="rounded-md border p-0.5 flex items-center gap-0.5">
            <Button
              variant={modeAffichage === "semaine" ? "default" : "ghost"}
              size="sm"
              onClick={() => setModeAffichage("semaine")}
            >
              Semaine
            </Button>
            <Button
              variant={modeAffichage === "mois" ? "default" : "ghost"}
              size="sm"
              onClick={() => setModeAffichage("mois")}
            >
              Mois
            </Button>
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={() => {
              if (modeAffichage === "semaine") {
                setOffsetSemaine((o) => o - 1);
              } else {
                setOffsetMois((o) => o - 1);
              }
            }}
            aria-label="Semaine précédente"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setOffsetSemaine(0);
              setOffsetMois(0);
            }}
          >
            Aujourd'hui
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => {
              if (modeAffichage === "semaine") {
                setOffsetSemaine((o) => o + 1);
              } else {
                setOffsetMois((o) => o + 1);
              }
            }}
            aria-label="Semaine suivante"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <div className="w-px h-6 bg-border hidden sm:block" />
          <Button
            variant="default"
            size="sm"
            onClick={() => genererIA(undefined)}
            disabled={enGeneration}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            {enGeneration ? "Génération..." : "Générer IA"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              if (!planning?.planning_id) {
                toast.error("Planning non persisté: générez un planning avant export PDF");
                return;
              }
              exporterPlanningPdf(planning.planning_id).catch(() => toast.error("Erreur d'export PDF"));
            }}
            title="Exporter en PDF"
          >
            <Download className="mr-2 h-4 w-4" />
            PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => exporterPlanningIcal(2).catch(() => toast.error("Erreur d'export"))}
            title="Exporter en iCalendar"
          >
            <Download className="mr-2 h-4 w-4" />
            iCal
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => genererCourses(undefined)}
            disabled={enGenerationCourses}
            title="Générer la liste de courses depuis le planning"
          >
            <ShoppingCart className="mr-2 h-4 w-4" />
            {enGenerationCourses ? "Génération..." : "Courses"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setChoixModePrepa(true)}
            disabled={!planning}
            title="Mode préparation — batch cooking ou jour par jour"
          >
            <CookingPot className="mr-2 h-4 w-4" />
            Préparation
          </Button>
        </div>
      </div>

      <CarteModeInvites
        contexte={modeInvites}
        onChange={mettreAJourModeInvites}
        onReset={reinitialiserModeInvites}
        suggestionsEvenements={suggestionsInvites}
        description="Adaptez le nombre de portions, la génération IA et la liste de courses pour une réception ou un repas élargi."
      />

      {/* ─── Grille Planning ─── */}
      {modeAffichage === "mois" ? (
        chargementMensuel ? (
          <Skeleton className="h-[520px] w-full" />
        ) : planningMensuel ? (
          <CalendrierMensuel mois={planningMensuel.mois} parJour={planningMensuel.par_jour} />
        ) : null
      ) : isLoading ? (
        <div className="grid gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {datesSemaine.map((date, idx) => {
            const dateObj = new Date(date);
            const estAujourdhui =
              date === new Date().toISOString().split("T")[0];

            return (
              <Card
                key={date}
                className={estAujourdhui ? "border-primary" : ""}
              >
                <CardHeader className="py-2 px-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">
                      {JOURS[idx]}{" "}
                      <span className="text-muted-foreground font-normal">
                        {dateObj.toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                    </CardTitle>
                    {estAujourdhui && (
                      <Badge variant="default" className="text-xs">
                        Aujourd'hui
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="py-2 px-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {TYPES_REPAS.map(({ valeur, label, emoji }) => {
                      const repas = trouverRepas(date, valeur);
                      const estCibleDrop =
                        !!repasGlisse &&
                        (repasGlisse.date_repas || repasGlisse.date || "").split("T")[0] !== date;

                      return (
                        <div
                          key={valeur}
                          className={`min-h-[48px] rounded-md border border-dashed p-2 text-xs transition-colors ${
                            estCibleDrop
                              ? "border-primary/40 bg-primary/5"
                              : "border-muted-foreground/25"
                          }`}
                          onDragOver={(e) => {
                            if (repasGlisse) {
                              e.preventDefault();
                              e.dataTransfer.dropEffect = "move";
                            }
                          }}
                          onDrop={() => deplacerRepas(date, valeur)}
                        >
                          <div className="text-muted-foreground mb-1">
                            {emoji} {label}
                          </div>
                          {repas ? (
                            <div
                              className="flex items-center justify-between gap-1"
                              draggable
                              onDragStart={(e) => {
                                setRepasGlisse(repas);
                                e.dataTransfer.effectAllowed = "move";
                              }}
                              onDragEnd={() => setRepasGlisse(null)}
                            >
                              <div className="flex items-center gap-1 min-w-0">
                                <span className="font-medium text-foreground truncate">
                                  {repas.recette_nom || repas.notes || "—"}
                                </span>
                                {repas.nutri_score && (
                                  <BadgeNutriscore grade={repas.nutri_score} />
                                )}
                              </div>
                              <div className="flex items-center gap-0.5 shrink-0">
                                <ConvertisseurInline className="h-5 px-1" />
                                <Button
                                  asChild
                                  variant="ghost"
                                  size="icon"
                                  className="h-5 w-5"
                                  title="Lancer un minuteur lié à ce repas"
                                >
                                  <a
                                    href={`/outils/minuteur?repas=${encodeURIComponent(
                                      repas.recette_nom || repas.notes || label
                                    )}&duree=${repas.type_repas === "diner" ? 35 : repas.type_repas === "dejeuner" ? 30 : 15}`}
                                    aria-label="Ouvrir le minuteur pour ce repas"
                                  >
                                    <Clock className="h-3 w-3" />
                                  </a>
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-5 w-5"
                                  onClick={() => retirerRepas(repas.id)}
                                  aria-label="Retirer le repas"
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-full text-xs"
                              onClick={() => ouvrirDialogue(date, valeur)}
                            >
                              <Plus className="h-3 w-3 mr-1" />
                              Ajouter
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {conflits && conflits.items.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">⚠️ Conflits détectés</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">{conflits.resume}</p>
            {conflits.items.slice(0, 5).map((conflit, index) => (
              <div key={`${conflit.date_jour}-${index}`} className="rounded-md border p-3">
                <p className="text-sm font-medium">{conflit.message}</p>
                {conflit.suggestion && (
                  <p className="text-xs text-muted-foreground mt-0.5">Suggestion: {conflit.suggestion}</p>
                )}
                <div className="mt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => toast.info("Aide à la résolution rapide bientôt disponible")}
                  >
                    Résoudre rapidement
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* ─── Nutrition hebdomadaire ─── */}
      {nutrition && nutrition.totaux.calories > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">🥗 Nutrition de la semaine</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="text-center rounded-md bg-orange-50 dark:bg-orange-950/20 p-2">
                <p className="text-2xl font-bold text-orange-600">{nutrition.totaux.calories}</p>
                <p className="text-xs text-muted-foreground">kcal total</p>
              </div>
              <div className="text-center rounded-md bg-blue-50 dark:bg-blue-950/20 p-2">
                <p className="text-2xl font-bold text-blue-600">{nutrition.totaux.proteines}g</p>
                <p className="text-xs text-muted-foreground">Protéines</p>
              </div>
              <div className="text-center rounded-md bg-yellow-50 dark:bg-yellow-950/20 p-2">
                <p className="text-2xl font-bold text-yellow-600">{nutrition.totaux.glucides}g</p>
                <p className="text-xs text-muted-foreground">Glucides</p>
              </div>
              <div className="text-center rounded-md bg-green-50 dark:bg-green-950/20 p-2">
                <p className="text-2xl font-bold text-green-600">{nutrition.totaux.lipides}g</p>
                <p className="text-xs text-muted-foreground">Lipides</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Moy. {nutrition.moyenne_calories_par_jour} kcal/jour
              {nutrition.nb_repas_sans_donnees > 0 && (
                <span> · {nutrition.nb_repas_sans_donnees} repas sans données</span>
              )}
            </p>
          </CardContent>
        </Card>
      )}

      {/* ─── Dialogue ajout repas avec sélecteur de recettes ─── */}
      <Dialog open={dialogueOuvert} onOpenChange={setDialogueOuvert}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Ajouter un repas</DialogTitle>
          </DialogHeader>
          {repasEnCours && (
            <p className="text-sm text-muted-foreground -mt-2">
              {JOURS[datesSemaine.indexOf(repasEnCours.date)]}{" "}
              {new Date(repasEnCours.date).toLocaleDateString("fr-FR", {
                day: "numeric",
                month: "long",
              })}{" "}
              — {TYPES_REPAS.find((t) => t.valeur === repasEnCours.type_repas)?.emoji}{" "}
              {TYPES_REPAS.find((t) => t.valeur === repasEnCours.type_repas)?.label}
            </p>
          )}
          <Tabs value={ongletDialogue} onValueChange={(v) => setOngletDialogue(v as "suggestions" | "libre")}>
            <TabsList className="w-full">
              <TabsTrigger value="suggestions" className="flex-1">
                <Search className="h-3.5 w-3.5 mr-1.5" />
                Recettes
              </TabsTrigger>
              <TabsTrigger value="libre" className="flex-1">
                <Plus className="h-3.5 w-3.5 mr-1.5" />
                Texte libre
              </TabsTrigger>
            </TabsList>

            {/* ─── Onglet suggestions de recettes ─── */}
            <TabsContent value="suggestions" className="space-y-3 mt-3">
              <div className="flex gap-2">
                <Input
                  placeholder="Rechercher une recette..."
                  value={rechercheRecette}
                  onChange={(e) => setRechercheRecette(e.target.value)}
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  size="sm"
                  title="Surprise du chef — choisit une recette au hasard"
                  disabled={!suggestions || suggestions.length === 0 || enAjout}
                  onClick={() => {
                    if (!suggestions || suggestions.length === 0) return;
                    const idx = Math.floor(Math.random() * suggestions.length);
                    choisirRecette(suggestions[idx]);
                  }}
                >
                  🎲
                </Button>
              </div>
              <div className="max-h-64 overflow-y-auto space-y-1.5">
                {chargeSuggestions ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <Skeleton key={i} className="h-14 w-full" />
                  ))
                ) : suggestionsFiltrees.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-6">
                    Aucune recette trouvée
                  </p>
                ) : (
                  suggestionsFiltrees.map((recette) => (
                    <button
                      key={recette.id}
                      onClick={() => choisirRecette(recette)}
                      disabled={enAjout}
                      className="w-full flex items-center justify-between rounded-md border p-3 text-left hover:bg-accent transition-colors disabled:opacity-50"
                    >
                      <div className="min-w-0">
                        <p className="font-medium text-sm truncate">{recette.nom}</p>
                        {recette.categorie && (
                          <Badge variant="outline" className="text-[10px] mt-0.5">
                            {recette.categorie}
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2 shrink-0 ml-2">
                        {recette.temps_total > 0 && (
                          <span className="text-xs text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {recette.temps_total} min
                          </span>
                        )}
                        <ConvertisseurInline />
                      </div>
                    </button>
                  ))
                )}
              </div>
            </TabsContent>

            {/* ─── Onglet texte libre ─── */}
            <TabsContent value="libre" className="space-y-4 mt-3">
              <Input
                value={notesRepas}
                onChange={(e) => setNotesRepas(e.target.value)}
                placeholder="Ex: Quiche lorraine"
              />
              <div className="flex justify-end gap-2">
                <Button
                  variant="outline"
                  onClick={() => setDialogueOuvert(false)}
                >
                  Annuler
                </Button>
                <Button
                  disabled={enAjout || !notesRepas.trim()}
                  onClick={() => {
                    if (repasEnCours) {
                      ajouterRepas({
                        date: repasEnCours.date,
                        type_repas: repasEnCours.type_repas,
                        notes: notesRepas,
                      });
                    }
                  }}
                >
                  {enAjout && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Ajouter
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      {/* ─── Dialogue résultat courses ─── */}
      <Dialog open={coursesDialogue} onOpenChange={setCoursesDialogue}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>🛒 Liste de courses générée</DialogTitle>
          </DialogHeader>
          {coursesResultat && (
            <div className="space-y-4">
              <div className="text-sm space-y-1">
                <p className="font-medium">
                  ✅ {coursesResultat.total_articles} articles ajoutés
                </p>
                {coursesResultat.contexte && coursesResultat.contexte.nb_invites > 0 && (
                  <p className="text-muted-foreground">
                    👥 Quantités ajustées pour {coursesResultat.contexte.nb_invites} invité(s)
                  </p>
                )}
                {coursesResultat.articles_en_stock > 0 && (
                  <p className="text-muted-foreground">
                    📦 {coursesResultat.articles_en_stock} articles déjà en stock (non ajoutés)
                  </p>
                )}
              </div>
              {Object.keys(coursesResultat.par_rayon).length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium">Par rayon :</p>
                  <div className="grid grid-cols-2 gap-1">
                    {Object.entries(coursesResultat.par_rayon).map(([rayon, count]) => (
                      <div key={rayon} className="flex items-center justify-between text-sm rounded-md bg-muted/50 px-2 py-1">
                        <span className="capitalize truncate">{rayon.replace(/_/g, " ")}</span>
                        <Badge variant="secondary" className="ml-1 text-xs">{count}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setCoursesDialogue(false)}>
                  Fermer
                </Button>
                <Button
                  onClick={() => {
                    setCoursesDialogue(false);
                    window.location.href = `/cuisine/courses`;
                  }}
                >
                  Voir la liste
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* ─── Dialogue résultat batch ─── */}
      <Dialog open={batchDialogue} onOpenChange={setBatchDialogue}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>🍳 Session batch créée</DialogTitle>
          </DialogHeader>
          {batchResultat && (
            <div className="space-y-4">
              <div className="text-sm space-y-1">
                <p className="font-medium">
                  ✅ {batchResultat.nom}
                </p>
                <p className="text-muted-foreground">
                  📖 {batchResultat.nb_recettes} recette{batchResultat.nb_recettes > 1 ? "s" : ""} sélectionnée{batchResultat.nb_recettes > 1 ? "s" : ""}
                </p>
                <p className="text-muted-foreground">
                  ⏱️ Durée estimée : {batchResultat.duree_estimee} minutes
                </p>
              </div>
              {batchResultat.robots_utilises.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium">Robots compatibles :</p>
                  <div className="flex flex-wrap gap-1">
                    {batchResultat.robots_utilises.map((robot) => (
                      <Badge key={robot} variant="outline" className="text-xs">
                        {robot}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              {batchResultat.recettes.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium">Recettes :</p>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {batchResultat.recettes.map((r) => (
                      <div
                        key={r.id}
                        className="text-sm rounded-md bg-muted/50 px-2 py-1"
                      >
                        {r.nom} ({r.portions} portions)
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setBatchDialogue(false)}>
                  Fermer
                </Button>
                <Button
                  onClick={() => {
                    setBatchDialogue(false);
                    window.location.href = `/cuisine/batch-cooking/${batchResultat.session_id}`;
                  }}
                >
                  Voir la session
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
      {/* ─── Dialog choix mode préparation ─── */}
      <Dialog open={choixModePrepa} onOpenChange={setChoixModePrepa}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>🍳 Mode de préparation</DialogTitle>
          </DialogHeader>
          <div className="space-y-3 pt-2">
            <p className="text-sm text-muted-foreground">
              Choisissez comment vous souhaitez préparer les repas de cette semaine.
            </p>

            {/* Option 1 : Batch cooking */}
            <button
              className="w-full text-left rounded-lg border p-4 hover:bg-accent transition-colors group"
              onClick={() => {
                setChoixModePrepa(false);
                genererBatch(undefined);
              }}
              disabled={enGenerationBatch}
            >
              <div className="flex items-start gap-3">
                <div className="rounded-md bg-primary/10 p-2 group-hover:bg-primary/20 transition-colors shrink-0">
                  <CookingPot className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Batch Cooking</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Préparez tout en une seule session le week-end. Idéal pour gagner du temps en semaine.
                  </p>
                  {enGenerationBatch && (
                    <p className="text-xs text-primary mt-1 flex items-center gap-1">
                      <Loader2 className="h-3 w-3 animate-spin" />
                      Génération en cours…
                    </p>
                  )}
                </div>
              </div>
            </button>

            {/* Option 2 : Jour par jour */}
            <button
              className="w-full text-left rounded-lg border p-4 hover:bg-accent transition-colors group"
              onClick={() => {
                setChoixModePrepa(false);
                window.location.href = "/cuisine/ma-semaine";
              }}
            >
              <div className="flex items-start gap-3">
                <div className="rounded-md bg-orange-100 dark:bg-orange-900/30 p-2 group-hover:bg-orange-200 dark:group-hover:bg-orange-900/50 transition-colors shrink-0">
                  <CalendarDays className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <p className="font-semibold text-sm">Jour par jour</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Suivez le wizard "Ma Semaine" pour préparer chaque jour avec flexibilité.
                  </p>
                </div>
              </div>
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
