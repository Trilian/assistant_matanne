// ═══════════════════════════════════════════════════════════
// Planning Repas — Grille hebdomadaire unifiée
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo, useCallback, lazy, Suspense, type ReactNode } from "react";
import {
  ChevronDown,
  X,
  Loader2,
  GripVertical,
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
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/composants/ui/sheet";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/composants/ui/tabs";
import {
  utiliserRequete,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  obtenirPlanningSemaine,
  obtenirPlanningMensuel,
  obtenirConflitsPlanning,
  mettreAJourRepas,
  obtenirSuggestionsAccompagnements,
  exporterPlanningIcal,
  exporterPlanningPdf,
  obtenirNutritionHebdo,
  obtenirSuggestionsRapides,
} from "@/bibliotheque/api/planning";
import { toast } from "sonner";
import type { GenererCoursesResult } from "@/bibliotheque/api/courses";
import type { GenererSessionDepuisPlanningResult } from "@/types/batch-cooking";
import type {
  TypeRepas,
  RepasPlanning,
  CreerRepasPlanningDTO,
  SuggestionRecettePlanning,
} from "@/types/planning";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { CalendrierMensuel } from "@/composants/planning/calendrier-mensuel";
import { CalendrierMosaiqueRepas } from "@/composants/planning/calendrier-mosaique-repas";
import { CalendrierColonnesPlanning } from "@/composants/planning/calendrier-colonnes-planning";
import { EnTetePlanning } from "@/composants/planning/en-tete-planning";
import {
  SectionAnalyseIaPlanning,
  ContenuDialogueCoursesPlanning,
  ContenuDialogueBatchPlanning,
  ContenuDialogueModePreparationPlanning,
} from "@/composants/planning/blocs-planning";
import { DialogueAjoutRepasPlanning } from "@/composants/planning/dialogue-ajout-repas-planning";
import { BanniereBrouillonConflits } from "@/composants/planning/banniere-brouillon-conflits";
import { CaseRepasPlanning } from "@/composants/planning/case-repas-planning";
import { type AnalysePlanningIaResultat } from "@/composants/planning/panneau-analyse-ia";
import { utiliserModeInvites } from "@/crochets/utiliser-mode-invites";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { utiliserPlanningNavigation } from "@/crochets/utiliser-planning-navigation";
import { utiliserPlanningDialogue } from "@/crochets/utiliser-planning-dialogue";
import { utiliserPresencePlanning } from "@/crochets/utiliser-presence-planning";
import { utiliserPlanningMutations } from "@/crochets/utiliser-planning-mutations";
import { utiliserPlanningDnd } from "@/crochets/utiliser-planning-dnd";
import { listerEvenementsFamiliaux } from "@/bibliotheque/api/famille";
import { listerEvenements } from "@/bibliotheque/api/calendriers";
import { obtenirFluxCuisine } from "@/bibliotheque/api/ia-bridges";
import { useIsMobile } from "@/crochets/use-mobile";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  closestCenter,
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { ModalGenerationPlanning } from "@/composants/cuisine/modal-generation-planning";

const ContenuNutritionLazy = lazy(() => import("../nutrition/page"));
const ContenuMaSemaineLazy = lazy(() => import("../ma-semaine/page"));
const ContenuSaisonnierLazy = lazy(() => import("../saisonnier/page"));

const STAGGER_DELAYS = ["delay-0", "delay-75", "delay-150", "delay-200", "delay-300", "delay-500", "delay-700"];
const TYPES_REPAS: { valeur: TypeRepas; label: string; emoji: string }[] = [
  { valeur: "petit_dejeuner", label: "Petit-déj", emoji: "🌅" },
  { valeur: "dejeuner", label: "Déjeuner", emoji: "☀️" },
  { valeur: "gouter", label: "Goûter", emoji: "🍪" },
  { valeur: "diner", label: "Dîner", emoji: "🌙" },
];

function ResponsiveOverlay({
  open,
  onOpenChange,
  title,
  children,
  contentClassName,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  children: ReactNode;
  contentClassName?: string;
}) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent
          side="bottom"
          className={`max-h-[92vh] overflow-y-auto rounded-t-3xl border-x-0 border-b-0 px-0 ${contentClassName ?? ""}`}
        >
          <SheetHeader className="pb-2">
            <SheetTitle>{title}</SheetTitle>
          </SheetHeader>
          <div className="px-4 pb-4">{children}</div>
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={contentClassName}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {children}
      </DialogContent>
    </Dialog>
  );
}

export default function PagePlanning() {
  const [vuePlanning, setVuePlanning] = useState<"planning" | "ma-semaine" | "nutrition" | "saisonnier">("planning");
  const { contexte: modeInvites, mettreAJour: mettreAJourModeInvites, reinitialiser: reinitialiserModeInvites } = utiliserModeInvites();
  const { utilisateur } = utiliserAuth();
  const {
    modeAffichage,
    setModeAffichage,
    setOffsetSemaine,
    dateDebut,
    datesSemaine,
    jours,
    moisSelectionne,
    moisLabel,
    moisLabelComplet,
    jourDebutSemaine,
    setJourDebutSemaine,
    reinitialiserPeriode,
    allerPrecedent,
    allerSuivant,
  } = utiliserPlanningNavigation();
  const {
    dialogueOuvert,
    setDialogueOuvert,
    repasEnCours,
    notesRepas,
    setNotesRepas,
    ongletDialogue,
    setOngletDialogue,
    rechercheRecette,
    setRechercheRecette,
    repasIdCree,
    setRepasIdCree,
    dialogueEtape,
    setDialogueEtape,
    legumesForm,
    setLegumesForm,
    feculentsForm,
    setFeculentsForm,
    proteineForm,
    setProteineForm,
    laitageForm,
    setLaitageForm,
    dessertForm,
    setDessertForm,
    fruitGouter,
    setFruitGouter,
    gateauGouter,
    setGateauGouter,
    nomRepasAjoute,
    setNomRepasAjoute,
    suggestionsIA,
    setSuggestionsIA,
    enSuggestionIA,
    setEnSuggestionIA,
    ouvrirDialogue,
    reinitialiserDialogue,
  } = utiliserPlanningDialogue();
  const [coursesDialogue, setCoursesDialogue] = useState(false);
  const [coursesResultat, setCoursesResultat] = useState<GenererCoursesResult | null>(null);
  const [batchDialogue, setBatchDialogue] = useState(false);
  const [batchResultat, setBatchResultat] = useState<GenererSessionDepuisPlanningResult | null>(null);
  const [choixModePrepa, setChoixModePrepa] = useState(false);
  const [analysePlanningIa, setAnalysePlanningIa] = useState<AnalysePlanningIaResultat | null>(null);
  const [modalGenerationOuvert, setModalGenerationOuvert] = useState(false);
  const [modalGenerationInitialPlats, setModalGenerationInitialPlats] = useState<string[]>([]);
  const [vuesSupplementairesOuvertes, setVuesSupplementairesOuvertes] = utiliserStockageLocal<boolean>("planning.vuesSupplementaires", false);
  const [nbPersonnesBase, setNbPersonnesBase] = utiliserStockageLocal<number>("planning.nbPersonnes", 2);
  // Panneau invités : ouvert uniquement si l'utilisateur l'active, fermé par défaut
  const [panneauInvitesOuvert, setPanneauInvitesOuvert] = utiliserStockageLocal<boolean>("planning.panneauInvites", false);
  // Message d'erreur IA affiché sous le bouton "Générer IA" (plus fiable qu'un toast)
  const [erreurIA, setErreurIA] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 6,
      },
    })
  );

  const invalider = utiliserInvalidation();
  const {
    identifiantPresencePlanning,
    synchroPlanningActive,
    diffuserPlanning,
    modeSynchroPlanning,
  } = utiliserPresencePlanning(utilisateur, dateDebut, invalider);

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
    () => listerEvenementsFamiliaux(),
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

  const { data: fluxCuisine } = utiliserRequete(
    ["flux", "cuisine", planning?.planning_id ? String(planning.planning_id) : "courant"],
    () => obtenirFluxCuisine(planning?.planning_id),
    { staleTime: 30 * 1000 }
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

  const nomDinerParDescription = useMemo(() => {
    const map: Record<string, string> = {};
    for (let i = 0; i < datesSemaine.length; i++) {
      const dateKey = datesSemaine[i];
      const jourNom = jours[i];
      const diner = planning?.repas?.find(
        (r) => (r.date_repas || r.date || "").split("T")[0] === dateKey && r.type_repas === "diner"
      );
      if (diner) {
        map[`dîner de ${jourNom}`] = diner.recette_nom || diner.notes || "";
      }
    }
    return map;
  }, [planning?.repas, datesSemaine, jours]);

  const planningPourAnalyseIa = useMemo(() => {
    return datesSemaine
      .map((date, index) => {
        const repasDuJour = repasParJour[date] ?? [];
        const trouverLibelle = (type: TypeRepas) => {
          const repas = repasDuJour.find((item) => item.type_repas === type);
          return repas?.recette_nom || repas?.notes || "";
        };

        return {
          jour: jours[index].toLowerCase(),
          petit_dej: trouverLibelle("petit_dejeuner"),
          midi: trouverLibelle("dejeuner"),
          soir: trouverLibelle("diner"),
        };
      })
      .filter((jour) => Boolean(jour.petit_dej || jour.midi || jour.soir));
  }, [datesSemaine, repasParJour]);

  const {
    repasGlisse,
    setRepasGlisse,
    handleDragStart,
    handleDragEnd,
  } = utiliserPlanningDnd({
    repasPlanning: planning?.repas,
    identifiantPresencePlanning,
    diffuserPlanning,
  });

  const {
    ajouterRepas,
    enAjout,
    retirerRepas,
    modifierChampRepas,
    lancerGenerationIA,
    enGeneration,
    genererCourses,
    enGenerationCourses,
    analyserPlanningIA,
    enAnalysePlanningIA,
    validerBrouillonPlanning,
    enValidationPlanning,
    regenererBrouillonPlanning,
    enRegenerationPlanning,
    regenererUnRepas,
    enGenerationBatch,
    genererBatch,
  } = utiliserPlanningMutations({
    dateDebut,
    nbPersonnesBase,
    contexteInvitesActif,
    modeInvites,
    evenementsModeInvites,
    identifiantPresencePlanning,
    diffuserPlanning,
    setRepasIdCree,
    setDialogueEtape,
    setDialogueOuvert,
    setNotesRepas,
    setErreurIA,
    setCoursesResultat,
    setCoursesDialogue,
    planningPourAnalyseIa,
    setAnalysePlanningIa,
    planningId: planning?.planning_id,
    setBatchResultat,
    setBatchDialogue,
  });

  // Noms dédupliqués des déjeuners/dîners pour la section "Conserver" du modal
  const repasActuelsSemaine = useMemo(() => {
    const noms = datesSemaine.flatMap((date) =>
      (repasParJour[date] ?? [])
        .filter((r) => r.type_repas === "dejeuner" || r.type_repas === "diner")
        .map((r) => r.recette_nom || r.notes || "")
        .filter(Boolean)
    );
    return Array.from(new Set(noms));
  }, [datesSemaine, repasParJour]);

  function trouverRepas(date: string, type: TypeRepas): RepasPlanning | undefined {
    return repasParJour[date]?.find((r) => r.type_repas === type);
  }

  const choisirRecette = useCallback(
    (recette: SuggestionRecettePlanning) => {
      if (!repasEnCours) return;
      setNomRepasAjoute(recette.nom);
      ajouterRepas({
        date: repasEnCours.date,
        type_repas: repasEnCours.type_repas,
        recette_id: recette.id,
        notes: recette.nom,
      });
    },
    [repasEnCours, ajouterRepas]
  );

  const ajouterTexteLibre = useCallback(() => {
    if (!repasEnCours) return;
    setNomRepasAjoute(notesRepas);
    ajouterRepas({
      date: repasEnCours.date,
      type_repas: repasEnCours.type_repas,
      notes: notesRepas,
    });
  }, [repasEnCours, notesRepas, ajouterRepas]);

  const demanderSuggestionsAccompagnements = useCallback(async () => {
    if (!repasIdCree) return;
    setEnSuggestionIA(true);
    try {
      const s = await obtenirSuggestionsAccompagnements(repasIdCree);
      setSuggestionsIA(s);
      if (s.legumes[0]) setLegumesForm(s.legumes[0]);
      if (s.feculents[0]) setFeculentsForm(s.feculents[0]);
      if (s.proteines[0]) setProteineForm(s.proteines[0]);
    } catch {
      toast.error("Impossible de générer des suggestions");
    } finally {
      setEnSuggestionIA(false);
    }
  }, [repasIdCree, setEnSuggestionIA, setSuggestionsIA, setLegumesForm, setFeculentsForm, setProteineForm]);

  const passerEquilibre = useCallback(() => {
    invalider(["planning"]);
    setDialogueOuvert(false);
    setDialogueEtape("choisir");
    setRepasIdCree(null);
  }, [invalider, setDialogueOuvert, setDialogueEtape, setRepasIdCree]);

  const confirmerEquilibre = useCallback(async () => {
    if (!repasIdCree || !repasEnCours) return;
    const payload: Partial<CreerRepasPlanningDTO> =
      repasEnCours.type_repas === "gouter"
        ? {
            laitage: laitageForm || undefined,
            fruit_gouter: fruitGouter || undefined,
            gateau_gouter: gateauGouter || undefined,
          }
        : {
            legumes: legumesForm || undefined,
            feculents: feculentsForm || undefined,
            proteine_accompagnement: proteineForm || undefined,
            laitage: laitageForm || undefined,
            dessert: dessertForm || undefined,
          };
    try {
      await mettreAJourRepas(repasIdCree, payload);
      invalider(["planning"]);
      toast.success("Accompagnements enregistrés");
      setDialogueOuvert(false);
      setDialogueEtape("choisir");
      setRepasIdCree(null);
    } catch {
      toast.error("Impossible de sauvegarder les accompagnements");
    }
  }, [
    repasIdCree,
    repasEnCours,
    laitageForm,
    fruitGouter,
    gateauGouter,
    legumesForm,
    feculentsForm,
    proteineForm,
    dessertForm,
    invalider,
    setDialogueOuvert,
    setDialogueEtape,
    setRepasIdCree,
  ]);

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

  const resumePeriode =
    modeAffichage === "semaine"
      ? `${moisLabel} · du ${new Date(datesSemaine[0] ?? dateDebut).toLocaleDateString("fr-FR", {
          day: "numeric",
          month: "short",
        })} au ${new Date(datesSemaine[datesSemaine.length - 1] ?? dateDebut).toLocaleDateString("fr-FR", {
          day: "numeric",
          month: "short",
        })}`
      : `Vue mensuelle · ${moisLabelComplet}`;
  const totalCreneauxSemaine = datesSemaine.length * TYPES_REPAS.length;
  const repasPlanifies = planning?.repas?.length ?? 0;
  const creneauxLibres = Math.max(totalCreneauxSemaine - repasPlanifies, 0);
  const caloriesMoyennes = nutrition?.moyenne_calories_par_jour ?? null;
  const nbPersonnes = nbPersonnesBase + (contexteInvitesActif ? modeInvites.nbInvites : 0);
  const statsPlanning = [
    { label: "Repas planifiés", valeur: `${repasPlanifies}/${totalCreneauxSemaine}` },
    { label: "Créneaux libres", valeur: `${creneauxLibres}` },
    { label: "Calories moy.", valeur: caloriesMoyennes ? `${caloriesMoyennes} kcal/j` : "En calcul" },
  ];

  return (
    <div className="space-y-6">
      {/* ─── Onglets haut niveau ─── */}
      <Tabs value={vuePlanning} onValueChange={(v) => setVuePlanning(v as typeof vuePlanning)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="planning">📅 Planning</TabsTrigger>
          <TabsTrigger value="ma-semaine">🔄 Ma Semaine</TabsTrigger>
          <TabsTrigger value="nutrition">🥗 Nutrition</TabsTrigger>
          <TabsTrigger value="saisonnier">🌿 Saisonnier</TabsTrigger>
        </TabsList>

        <TabsContent value="ma-semaine" className="mt-4">
          <Suspense fallback={<div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}>
            <ContenuMaSemaineLazy />
          </Suspense>
        </TabsContent>

        <TabsContent value="nutrition" className="mt-4">
          <Suspense fallback={<div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}>
            <ContenuNutritionLazy />
          </Suspense>
        </TabsContent>

        <TabsContent value="saisonnier" className="mt-4">
          <Suspense fallback={<div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}>
            <ContenuSaisonnierLazy />
          </Suspense>
        </TabsContent>

        <TabsContent value="planning" className="mt-4 space-y-6">
      {/* ─── En-tête ─── */}
        <EnTetePlanning
          resumePeriode={resumePeriode}
          synchroPlanningActive={synchroPlanningActive}
          modeSynchroPlanning={modeSynchroPlanning}
          contexteInvitesActif={contexteInvitesActif}
          nbInvites={modeInvites.nbInvites}
          statsPlanning={statsPlanning}
          nbPersonnesBase={nbPersonnesBase}
          nbPersonnes={nbPersonnes}
          setNbPersonnesBase={setNbPersonnesBase}
          modeAffichage={modeAffichage}
          setModeAffichage={setModeAffichage}
          allerPrecedent={allerPrecedent}
          reinitialiserPeriode={reinitialiserPeriode}
          jourDebutSemaine={jourDebutSemaine}
          setJourDebutSemaine={setJourDebutSemaine}
          setOffsetSemaine={setOffsetSemaine}
          nomsJoursSemaine={[
            "Dimanche",
            "Lundi",
            "Mardi",
            "Mercredi",
            "Jeudi",
            "Vendredi",
            "Samedi",
          ]}
          allerSuivant={allerSuivant}
          onOuvrirGenerationIa={() => {
            setErreurIA(null);
            setModalGenerationOuvert(true);
          }}
          enGeneration={enGeneration}
          onExporterPdf={() => {
            if (!planning?.planning_id) {
              toast.error("Planning non persisté: générez un planning avant export PDF");
              return;
            }
            exporterPlanningPdf(planning.planning_id).catch(() => toast.error("Erreur d'export PDF"));
          }}
          onExporterIcal={() => exporterPlanningIcal(2).catch(() => toast.error("Erreur d'export"))}
          onGenererCourses={() => genererCourses(undefined)}
          enGenerationCourses={enGenerationCourses}
          onOuvrirChoixModePrepa={() => setChoixModePrepa(true)}
          planningExiste={Boolean(planning)}
          onTogglePanneauInvites={() => setPanneauInvitesOuvert((v) => !v)}
          erreurIA={erreurIA}
          setErreurIA={setErreurIA}
        />

      {/* Mode invités — panneau collapsible, caché par défaut */}
      {panneauInvitesOuvert && (
        <CarteModeInvites
          contexte={modeInvites}
          onChange={(patch) => {
            mettreAJourModeInvites(patch);
            // Fermer automatiquement si on désactive le mode
            if (patch.actif === false) setPanneauInvitesOuvert(false);
          }}
          onReset={() => {
            reinitialiserModeInvites();
            setPanneauInvitesOuvert(false);
          }}
          suggestionsEvenements={suggestionsInvites}
          description="Adaptez le nombre de portions, la génération IA et la liste de courses pour une réception ou un repas élargi."
        />
      )}

      <BanniereBrouillonConflits
        fluxCuisine={fluxCuisine}
        conflits={conflits}
        enValidationPlanning={enValidationPlanning}
        enRegenerationPlanning={enRegenerationPlanning}
        validerBrouillonPlanning={validerBrouillonPlanning}
        regenererBrouillonPlanning={regenererBrouillonPlanning}
      />

      {/* ─── Grille Planning ─── */}
      {modeAffichage === "mois" ? (
        chargementMensuel ? (
          <Skeleton className="h-[520px] w-full" />
        ) : planningMensuel ? (
          <div className="animate-in fade-in slide-in-from-bottom-1 duration-500">
            <CalendrierMensuel mois={planningMensuel.mois} parJour={planningMensuel.par_jour} />
          </div>
        ) : null
      ) : isLoading ? (
        <div className="grid gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} className={`h-24 w-full animate-in fade-in slide-in-from-bottom-1 duration-500 ${STAGGER_DELAYS[i % STAGGER_DELAYS.length]}`} />
          ))}
        </div>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
          onDragCancel={() => setRepasGlisse(null)}
        >
          <div className="space-y-2" data-planning-grid>
            <div className="rounded-2xl border border-dashed bg-muted/35 px-3 py-2 text-xs text-muted-foreground">
              <span className="font-medium text-foreground/80">Astuce :</span> utilisez la poignée <GripVertical className="inline h-3 w-3" /> pour déplacer un repas par glisser-déposer, y compris sur mobile.
            </div>
            {datesSemaine.map((date, idx) => {
              const dateObj = new Date(date);
              const estAujourdhui =
                date === new Date().toISOString().split("T")[0];

              return (
                <Card
                  key={date}
                  className={`${estAujourdhui ? "border-primary" : ""} animate-in fade-in slide-in-from-bottom-1 duration-500 ${STAGGER_DELAYS[idx % STAGGER_DELAYS.length]}`}
                >
                  <CardHeader className="py-2 px-4">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium">
                        {jours[idx]}{" "}
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
                      {TYPES_REPAS.map(({ valeur, label, emoji }) => (
                        <CaseRepasPlanning
                          key={valeur}
                          date={date}
                          type={valeur}
                          label={label}
                          emoji={emoji}
                          repas={trouverRepas(date, valeur)}
                          repasGlisse={repasGlisse}
                          onAjouter={ouvrirDialogue}
                          onRetirer={retirerRepas}
                          onModifierChamp={modifierChampRepas}
                          onRegenerer={(repas) => regenererUnRepas(repas.id)}
                          nomDinerParDescription={nomDinerParDescription}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          <DragOverlay>
            {repasGlisse ? (
              <div className="rounded-md border bg-background px-3 py-2 text-sm shadow-xl">
                {repasGlisse.recette_nom || repasGlisse.notes || "Repas"}
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      )}

      {modeAffichage === "semaine" && !isLoading && (
        <div className="animate-in fade-in slide-in-from-bottom-1 duration-500 delay-300">
          <button
            type="button"
            onClick={() => setVuesSupplementairesOuvertes(!vuesSupplementairesOuvertes)}
            className="flex w-full items-center justify-between rounded-xl border border-dashed bg-muted/30 px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground"
          >
            <span className="font-medium">Vues supplémentaires — mosaïque &amp; colonnes</span>
            <ChevronDown
              className={`h-4 w-4 shrink-0 transition-transform duration-200 ${
                vuesSupplementairesOuvertes ? "rotate-180" : ""
              }`}
            />
          </button>
          {vuesSupplementairesOuvertes && (
            <div className="mt-3 space-y-4">
              <CalendrierMosaiqueRepas dates={datesSemaine} repasParJour={repasParJour} />
              <CalendrierColonnesPlanning dates={datesSemaine} repasParJour={repasParJour} />
            </div>
          )}
        </div>
      )}

      {modeAffichage === "semaine" && (
        <SectionAnalyseIaPlanning
          analysePlanningIa={analysePlanningIa}
          enAnalysePlanningIA={enAnalysePlanningIA}
          nbLignesAnalyse={planningPourAnalyseIa.length}
          onAnalyser={() => analyserPlanningIA(undefined)}
          onRegenererAvecConseils={(platsSuggeres) => {
            setErreurIA(null);
            setModalGenerationInitialPlats(platsSuggeres);
            setModalGenerationOuvert(true);
          }}
        />
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
      <ResponsiveOverlay
        open={dialogueOuvert}
        onOpenChange={(open) => {
          setDialogueOuvert(open);
          if (!open) {
            reinitialiserDialogue();
          }
        }}
        title={dialogueEtape === "equilibre" ? "⚖ Équilibre du repas" : "Ajouter un repas"}
        contentClassName="sm:max-w-lg"
      >
        <DialogueAjoutRepasPlanning
          repasEnCours={repasEnCours}
          jours={jours}
          datesSemaine={datesSemaine}
          typesRepas={TYPES_REPAS}
          dialogueEtape={dialogueEtape}
          ongletDialogue={ongletDialogue}
          setOngletDialogue={setOngletDialogue}
          rechercheRecette={rechercheRecette}
          setRechercheRecette={setRechercheRecette}
          suggestions={suggestions}
          chargeSuggestions={chargeSuggestions}
          suggestionsFiltrees={suggestionsFiltrees}
          enAjout={enAjout}
          choisirRecette={choisirRecette}
          notesRepas={notesRepas}
          setNotesRepas={setNotesRepas}
          onAnnulerAjout={() => setDialogueOuvert(false)}
          onAjouterTexteLibre={ajouterTexteLibre}
          repasIdCree={repasIdCree}
          nomRepasAjoute={nomRepasAjoute}
          enSuggestionIA={enSuggestionIA}
          onDemanderSuggestions={demanderSuggestionsAccompagnements}
          suggestionsIA={suggestionsIA}
          legumesForm={legumesForm}
          setLegumesForm={setLegumesForm}
          feculentsForm={feculentsForm}
          setFeculentsForm={setFeculentsForm}
          proteineForm={proteineForm}
          setProteineForm={setProteineForm}
          laitageForm={laitageForm}
          setLaitageForm={setLaitageForm}
          dessertForm={dessertForm}
          setDessertForm={setDessertForm}
          fruitGouter={fruitGouter}
          setFruitGouter={setFruitGouter}
          gateauGouter={gateauGouter}
          setGateauGouter={setGateauGouter}
          onPasserEquilibre={passerEquilibre}
          onConfirmerEquilibre={confirmerEquilibre}
        />
      </ResponsiveOverlay>

      {/* ─── Dialogue résultat courses ─── */}
      <ResponsiveOverlay
        open={coursesDialogue}
        onOpenChange={setCoursesDialogue}
        title="🛒 Liste de courses générée"
        contentClassName="sm:max-w-md"
      >
        {coursesResultat && (
          <ContenuDialogueCoursesPlanning
            coursesResultat={coursesResultat}
            onFermer={() => setCoursesDialogue(false)}
            onVoirListe={() => {
              setCoursesDialogue(false);
              window.location.href = `/cuisine/courses`;
            }}
          />
        )}
      </ResponsiveOverlay>

      {/* ─── Dialogue résultat batch ─── */}
      <ResponsiveOverlay
        open={batchDialogue}
        onOpenChange={setBatchDialogue}
        title="🍳 Session batch créée"
        contentClassName="sm:max-w-md"
      >
        {batchResultat && (
          <ContenuDialogueBatchPlanning
            batchResultat={batchResultat}
            onFermer={() => setBatchDialogue(false)}
            onVoirSession={() => {
              setBatchDialogue(false);
              window.location.href = `/cuisine/batch-cooking/${batchResultat.session_id}`;
            }}
          />
        )}
      </ResponsiveOverlay>
      {/* ─── Dialog choix mode préparation ─── */}
      <ResponsiveOverlay
        open={choixModePrepa}
        onOpenChange={setChoixModePrepa}
        title="🍳 Mode de préparation"
        contentClassName="sm:max-w-md"
      >
        <ContenuDialogueModePreparationPlanning
          enGenerationBatch={enGenerationBatch}
          onChoisirBatch={() => {
            setChoixModePrepa(false);
            genererBatch(undefined);
          }}
          onChoisirJourParJour={() => {
            setChoixModePrepa(false);
            window.location.href = "/cuisine/ma-semaine";
          }}
        />
      </ResponsiveOverlay>
        </TabsContent>
      </Tabs>

      {/* Modal de génération IA */}
      <ModalGenerationPlanning
        ouvert={modalGenerationOuvert}
        onFermer={() => {
          setModalGenerationOuvert(false);
          setModalGenerationInitialPlats([]);
        }}
        enGeneration={enGeneration}
        nbPersonnesInitial={nbPersonnesBase + (contexteInvitesActif ? modeInvites.nbInvites : 0)}
        dateDebut={dateDebut}
        initialPlats={modalGenerationInitialPlats}
        repasActuels={repasActuelsSemaine}
        onGenerer={(params) => {
          setModalGenerationOuvert(false);
          setModalGenerationInitialPlats([]);
          lancerGenerationIA(params);
        }}
      />
    </div>
  );
}
