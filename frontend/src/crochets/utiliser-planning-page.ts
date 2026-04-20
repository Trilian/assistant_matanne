// ═══════════════════════════════════════════════════════════
// Hook orchestrateur de la page Planning
// Centralise requêtes, état, mémos et callbacks
// ═══════════════════════════════════════════════════════════

import { useState, useMemo, useCallback } from "react";
import { utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
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
import { TYPES_REPAS } from "@/composants/planning/grille-planning-hebdo";

export function utiliserPlanningPage() {
  // ─── Tab vue ───
  const [vuePlanning, setVuePlanning] = useState<
    "planning" | "ma-semaine" | "nutrition" | "saisonnier"
  >("planning");
  const onChangeVuePlanning = useCallback((v: string) => {
    setVuePlanning(v as "planning" | "ma-semaine" | "nutrition" | "saisonnier");
  }, []);

  // ─── Sous-hooks ───
  const {
    contexte: modeInvites,
    mettreAJour: mettreAJourModeInvites,
    reinitialiser: reinitialiserModeInvites,
  } = utiliserModeInvites();
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

  // ─── État local ───
  const [coursesDialogue, setCoursesDialogue] = useState(false);
  const [coursesResultat, setCoursesResultat] = useState<GenererCoursesResult | null>(null);
  const [batchDialogue, setBatchDialogue] = useState(false);
  const [batchResultat, setBatchResultat] = useState<GenererSessionDepuisPlanningResult | null>(null);
  const [choixModePrepa, setChoixModePrepa] = useState(false);
  const [analysePlanningIa, setAnalysePlanningIa] = useState<AnalysePlanningIaResultat | null>(null);
  const [modalGenerationOuvert, setModalGenerationOuvert] = useState(false);
  const [modalGenerationInitialPlats, setModalGenerationInitialPlats] = useState<string[]>([]);
  const [vuesSupplementairesOuvertes, setVuesSupplementairesOuvertes] =
    utiliserStockageLocal<boolean>("planning.vuesSupplementaires", false);
  const [nbPersonnesBase, setNbPersonnesBase] = utiliserStockageLocal<number>(
    "planning.nbPersonnes",
    2
  );
  const [panneauInvitesOuvert, setPanneauInvitesOuvert] = utiliserStockageLocal<boolean>(
    "planning.panneauInvites",
    false
  );
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

  // ─── Computed ───
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
    const libellesCalendrier = (evenementsCalendrier ?? [])
      .map((item) => item.titre)
      .filter(Boolean);
    return Array.from(new Set([...libellesFamille, ...libellesCalendrier])).slice(0, 6);
  }, [evenementsCalendrier, evenementsFamille]);

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
        (r) =>
          (r.date_repas || r.date || "").split("T")[0] === dateKey && r.type_repas === "diner"
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
  }, [datesSemaine, repasParJour, jours]);

  // ─── DnD ───
  const { repasGlisse, setRepasGlisse, handleDragStart, handleDragEnd } = utiliserPlanningDnd({
    repasPlanning: planning?.repas,
    identifiantPresencePlanning,
    diffuserPlanning,
  });

  // ─── Mutations ───
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

  // ─── Helpers mémoisés ───
  const repasActuelsSemaine = useMemo(() => {
    const noms = datesSemaine.flatMap((date) =>
      (repasParJour[date] ?? [])
        .filter((r) => r.type_repas === "dejeuner" || r.type_repas === "diner")
        .map((r) => r.recette_nom || r.notes || "")
        .filter(Boolean)
    );
    return Array.from(new Set(noms));
  }, [datesSemaine, repasParJour]);

  const trouverRepas = useCallback(
    (date: string, type: TypeRepas): RepasPlanning | undefined =>
      repasParJour[date]?.find((r) => r.type_repas === type),
    [repasParJour]
  );

  const suggestionsFiltrees = useMemo(() => {
    if (!suggestions) return [];
    if (!rechercheRecette.trim()) return suggestions;
    const q = rechercheRecette.toLowerCase();
    return suggestions.filter(
      (s) => s.nom.toLowerCase().includes(q) || (s.categorie ?? "").toLowerCase().includes(q)
    );
  }, [suggestions, rechercheRecette]);

  // ─── Stats / résumé ───
  const resumePeriode =
    modeAffichage === "semaine"
      ? `${moisLabel} · du ${new Date(datesSemaine[0] ?? dateDebut).toLocaleDateString("fr-FR", {
          day: "numeric",
          month: "short",
        })} au ${new Date(
          datesSemaine[datesSemaine.length - 1] ?? dateDebut
        ).toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}`
      : `Vue mensuelle · ${moisLabelComplet}`;

  const nbPersonnes = nbPersonnesBase + (contexteInvitesActif ? modeInvites.nbInvites : 0);
  const repasPlanifies = planning?.repas?.length ?? 0;
  const totalCreneauxSemaine = datesSemaine.length * TYPES_REPAS.length;
  const creneauxLibres = Math.max(totalCreneauxSemaine - repasPlanifies, 0);
  const caloriesMoyennes = nutrition?.moyenne_calories_par_jour ?? null;
  const statsPlanning = [
    { label: "Repas planifiés", valeur: `${repasPlanifies}/${totalCreneauxSemaine}` },
    { label: "Créneaux libres", valeur: `${creneauxLibres}` },
    {
      label: "Calories moy.",
      valeur: caloriesMoyennes ? `${caloriesMoyennes} kcal/j` : "En calcul",
    },
  ];

  // ─── Callbacks EnTetePlanning ───
  const onOuvrirGenerationIa = useCallback(() => {
    setErreurIA(null);
    setModalGenerationOuvert(true);
  }, []);

  const onExporterPdf = useCallback(() => {
    if (!planning?.planning_id) {
      toast.error("Planning non persisté: générez un planning avant export PDF");
      return;
    }
    exporterPlanningPdf(planning.planning_id).catch(() => toast.error("Erreur d'export PDF"));
  }, [planning?.planning_id]);

  const onExporterIcal = useCallback(() => {
    exporterPlanningIcal(2).catch(() => toast.error("Erreur d'export"));
  }, []);

  const onGenererCourses = useCallback(() => genererCourses(undefined), [genererCourses]);

  const onOuvrirChoixModePrepa = useCallback(() => setChoixModePrepa(true), []);

  const onTogglePanneauInvites = useCallback(
    () => setPanneauInvitesOuvert((v) => !v),
    [setPanneauInvitesOuvert]
  );

  // ─── Callbacks dialogue ajout repas ───
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
    [repasEnCours, ajouterRepas, setNomRepasAjoute]
  );

  const ajouterTexteLibre = useCallback(() => {
    if (!repasEnCours) return;
    setNomRepasAjoute(notesRepas);
    ajouterRepas({
      date: repasEnCours.date,
      type_repas: repasEnCours.type_repas,
      notes: notesRepas,
    });
  }, [repasEnCours, notesRepas, ajouterRepas, setNomRepasAjoute]);

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
  }, [
    repasIdCree,
    setEnSuggestionIA,
    setSuggestionsIA,
    setLegumesForm,
    setFeculentsForm,
    setProteineForm,
  ]);

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

  // ─── Retour ───
  return {
    // Tab
    vuePlanning,
    onChangeVuePlanning,
    // Mode invités
    modeInvites,
    mettreAJourModeInvites,
    reinitialiserModeInvites,
    contexteInvitesActif,
    suggestionsInvites,
    panneauInvitesOuvert,
    setPanneauInvitesOuvert,
    onTogglePanneauInvites,
    // Navigation
    modeAffichage,
    setModeAffichage,
    setOffsetSemaine,
    dateDebut,
    datesSemaine,
    jours,
    jourDebutSemaine,
    setJourDebutSemaine,
    reinitialiserPeriode,
    allerPrecedent,
    allerSuivant,
    // Présence/sync
    synchroPlanningActive,
    modeSynchroPlanning,
    // Données planning
    isLoading,
    chargementMensuel,
    planningMensuel,
    planningExiste: Boolean(planning),
    fluxCuisine,
    conflits,
    nutrition,
    // Personnes & stats
    nbPersonnesBase,
    setNbPersonnesBase,
    nbPersonnes,
    statsPlanning,
    resumePeriode,
    // Erreur IA
    erreurIA,
    setErreurIA,
    // Modal génération IA
    modalGenerationOuvert,
    setModalGenerationOuvert,
    modalGenerationInitialPlats,
    setModalGenerationInitialPlats,
    repasActuelsSemaine,
    // Callbacks EnTete
    onOuvrirGenerationIa,
    onExporterPdf,
    onExporterIcal,
    onGenererCourses,
    enGenerationCourses,
    onOuvrirChoixModePrepa,
    // Dialogs résultats
    coursesDialogue,
    setCoursesDialogue,
    coursesResultat,
    batchDialogue,
    setBatchDialogue,
    batchResultat,
    choixModePrepa,
    setChoixModePrepa,
    enGenerationBatch,
    genererBatch,
    // DnD
    repasGlisse,
    setRepasGlisse,
    handleDragStart,
    handleDragEnd,
    // Mutations
    enAjout,
    enGeneration,
    lancerGenerationIA,
    retirerRepas,
    modifierChampRepas,
    regenererUnRepas,
    analyserPlanningIA,
    enAnalysePlanningIA,
    validerBrouillonPlanning,
    enValidationPlanning,
    regenererBrouillonPlanning,
    enRegenerationPlanning,
    // Computed
    repasParJour,
    nomDinerParDescription,
    planningPourAnalyseIa,
    analysePlanningIa,
    trouverRepas,
    // Dialogue ajout repas
    dialogueOuvert,
    setDialogueOuvert,
    reinitialiserDialogue,
    dialogueEtape,
    repasEnCours,
    ongletDialogue,
    setOngletDialogue,
    rechercheRecette,
    setRechercheRecette,
    suggestions,
    chargeSuggestions,
    suggestionsFiltrees,
    choisirRecette,
    notesRepas,
    setNotesRepas,
    ajouterTexteLibre,
    repasIdCree,
    nomRepasAjoute,
    enSuggestionIA,
    demanderSuggestionsAccompagnements,
    suggestionsIA,
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
    passerEquilibre,
    confirmerEquilibre,
    // Vues supplémentaires
    vuesSupplementairesOuvertes,
    setVuesSupplementairesOuvertes,
    ouvrirDialogue,
  };
}
