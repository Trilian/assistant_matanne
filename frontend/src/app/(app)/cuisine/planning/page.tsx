// ═══════════════════════════════════════════════════════════
// Planning Repas — Grille hebdomadaire unifiée
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo, useCallback, lazy, Suspense } from "react";
import {
  X,
  Loader2,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
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
import { EnTetePlanning } from "@/composants/planning/en-tete-planning";
import { SectionAnalyseIaPlanning } from "@/composants/planning/blocs-planning";
import { ResponsiveOverlay } from "@/composants/planning/responsive-overlay";
import { DialoguesResultatsPlanning } from "@/composants/planning/dialogues-resultats-planning";
import { DialogueAjoutRepasPlanning } from "@/composants/planning/dialogue-ajout-repas-planning";
import { BanniereBrouillonConflits } from "@/composants/planning/banniere-brouillon-conflits";
import { SectionNutritionHebdo } from "@/composants/planning/section-nutrition-hebdo";
import { VuesSupplementairesPlanning } from "@/composants/planning/vues-supplementaires-planning";
import {
  GrillePlanningHebdo,
  TYPES_REPAS,
} from "@/composants/planning/grille-planning-hebdo";
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

import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";

import { ModalGenerationPlanning } from "@/composants/cuisine/modal-generation-planning";

const ContenuNutritionLazy = lazy(() => import("../nutrition/page"));
const ContenuMaSemaineLazy = lazy(() => import("../ma-semaine/page"));
const ContenuSaisonnierLazy = lazy(() => import("../saisonnier/page"));

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
      <GrillePlanningHebdo
        modeAffichage={modeAffichage}
        chargementMensuel={chargementMensuel}
        planningMensuel={planningMensuel}
        isLoading={isLoading}
        repasGlisse={repasGlisse}
        setRepasGlisse={setRepasGlisse}
        handleDragStart={handleDragStart}
        handleDragEnd={handleDragEnd}
        datesSemaine={datesSemaine}
        jours={jours}
        trouverRepas={trouverRepas}
        onAjouter={ouvrirDialogue}
        onRetirer={retirerRepas}
        onModifierChamp={modifierChampRepas}
        onRegenerer={(repas) => regenererUnRepas(repas.id)}
        nomDinerParDescription={nomDinerParDescription}
      />

      {modeAffichage === "semaine" && !isLoading && (
        <VuesSupplementairesPlanning
          dates={datesSemaine}
          repasParJour={repasParJour}
          ouvert={vuesSupplementairesOuvertes}
          onToggle={() => setVuesSupplementairesOuvertes(!vuesSupplementairesOuvertes)}
        />
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

      <SectionNutritionHebdo nutrition={nutrition} />

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

      <DialoguesResultatsPlanning
        coursesDialogue={coursesDialogue}
        setCoursesDialogue={setCoursesDialogue}
        coursesResultat={coursesResultat}
        batchDialogue={batchDialogue}
        setBatchDialogue={setBatchDialogue}
        batchResultat={batchResultat}
        choixModePrepa={choixModePrepa}
        setChoixModePrepa={setChoixModePrepa}
        enGenerationBatch={enGenerationBatch}
        genererBatch={genererBatch}
      />
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
