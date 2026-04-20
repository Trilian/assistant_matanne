// ═══════════════════════════════════════════════════════════
// Planning Repas — Grille hebdomadaire unifiée
// ═══════════════════════════════════════════════════════════

"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { EnTetePlanning } from "@/composants/planning/en-tete-planning";
import { SectionAnalyseIaPlanning } from "@/composants/planning/blocs-planning";
import { DialoguesResultatsPlanning } from "@/composants/planning/dialogues-resultats-planning";
import { OverlayDialogueAjoutRepas } from "@/composants/planning/overlay-dialogue-ajout-repas";
import { BanniereBrouillonConflits } from "@/composants/planning/banniere-brouillon-conflits";
import { SectionNutritionHebdo } from "@/composants/planning/section-nutrition-hebdo";
import { VuesSupplementairesPlanning } from "@/composants/planning/vues-supplementaires-planning";
import { GrillePlanningHebdo } from "@/composants/planning/grille-planning-hebdo";
import { OngletsVuesSecondaires } from "@/composants/planning/onglets-vues-secondaires";
import { OverlayModalGenerationPlanning } from "@/composants/planning/overlay-modal-generation-planning";
import { utiliserPlanningPage } from "@/crochets/utiliser-planning-page";

const NOMS_JOURS_SEMAINE = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];

export default function PagePlanning() {
  const p = utiliserPlanningPage();

  return (
    <div className="space-y-6">
      <Tabs value={p.vuePlanning} onValueChange={p.onChangeVuePlanning}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="planning">📅 Planning</TabsTrigger>
          <TabsTrigger value="ma-semaine">🔄 Ma Semaine</TabsTrigger>
          <TabsTrigger value="nutrition">🥗 Nutrition</TabsTrigger>
          <TabsTrigger value="saisonnier">🌿 Saisonnier</TabsTrigger>
        </TabsList>

        <OngletsVuesSecondaires />

        <TabsContent value="planning" className="mt-4 space-y-6">
          <EnTetePlanning
            resumePeriode={p.resumePeriode}
            synchroPlanningActive={p.synchroPlanningActive}
            modeSynchroPlanning={p.modeSynchroPlanning}
            contexteInvitesActif={p.contexteInvitesActif}
            nbInvites={p.modeInvites.nbInvites}
            statsPlanning={p.statsPlanning}
            nbPersonnesBase={p.nbPersonnesBase}
            nbPersonnes={p.nbPersonnes}
            setNbPersonnesBase={p.setNbPersonnesBase}
            modeAffichage={p.modeAffichage}
            setModeAffichage={p.setModeAffichage}
            allerPrecedent={p.allerPrecedent}
            reinitialiserPeriode={p.reinitialiserPeriode}
            jourDebutSemaine={p.jourDebutSemaine}
            setJourDebutSemaine={p.setJourDebutSemaine}
            setOffsetSemaine={p.setOffsetSemaine}
            nomsJoursSemaine={NOMS_JOURS_SEMAINE}
            allerSuivant={p.allerSuivant}
            onOuvrirGenerationIa={p.onOuvrirGenerationIa}
            enGeneration={p.enGeneration}
            onExporterPdf={p.onExporterPdf}
            onExporterIcal={p.onExporterIcal}
            onGenererCourses={p.onGenererCourses}
            enGenerationCourses={p.enGenerationCourses}
            onOuvrirChoixModePrepa={p.onOuvrirChoixModePrepa}
            planningExiste={p.planningExiste}
            onTogglePanneauInvites={p.onTogglePanneauInvites}
            erreurIA={p.erreurIA}
            setErreurIA={p.setErreurIA}
          />

          {p.panneauInvitesOuvert && (
            <CarteModeInvites
              contexte={p.modeInvites}
              onChange={(patch) => {
                p.mettreAJourModeInvites(patch);
                if (patch.actif === false) p.setPanneauInvitesOuvert(false);
              }}
              onReset={() => {
                p.reinitialiserModeInvites();
                p.setPanneauInvitesOuvert(false);
              }}
              suggestionsEvenements={p.suggestionsInvites}
              description="Adaptez le nombre de portions, la génération IA et la liste de courses pour une réception ou un repas élargi."
            />
          )}

          <BanniereBrouillonConflits
            fluxCuisine={p.fluxCuisine}
            conflits={p.conflits}
            enValidationPlanning={p.enValidationPlanning}
            enRegenerationPlanning={p.enRegenerationPlanning}
            validerBrouillonPlanning={p.validerBrouillonPlanning}
            regenererBrouillonPlanning={p.regenererBrouillonPlanning}
          />

          <GrillePlanningHebdo
            modeAffichage={p.modeAffichage}
            chargementMensuel={p.chargementMensuel}
            planningMensuel={p.planningMensuel}
            isLoading={p.isLoading}
            repasGlisse={p.repasGlisse}
            setRepasGlisse={p.setRepasGlisse}
            handleDragStart={p.handleDragStart}
            handleDragEnd={p.handleDragEnd}
            datesSemaine={p.datesSemaine}
            jours={p.jours}
            trouverRepas={p.trouverRepas}
            onAjouter={p.ouvrirDialogue}
            onRetirer={p.retirerRepas}
            onModifierChamp={p.modifierChampRepas}
            onRegenerer={(repas) => p.regenererUnRepas(repas.id)}
            nomDinerParDescription={p.nomDinerParDescription}
          />

          {p.modeAffichage === "semaine" && !p.isLoading && (
            <VuesSupplementairesPlanning
              dates={p.datesSemaine}
              repasParJour={p.repasParJour}
              ouvert={p.vuesSupplementairesOuvertes}
              onToggle={() => p.setVuesSupplementairesOuvertes(!p.vuesSupplementairesOuvertes)}
            />
          )}

          {p.modeAffichage === "semaine" && (
            <SectionAnalyseIaPlanning
              analysePlanningIa={p.analysePlanningIa}
              enAnalysePlanningIA={p.enAnalysePlanningIA}
              nbLignesAnalyse={p.planningPourAnalyseIa.length}
              onAnalyser={() => p.analyserPlanningIA(undefined)}
              onRegenererAvecConseils={(platsSuggeres) => {
                p.setErreurIA(null);
                p.setModalGenerationInitialPlats(platsSuggeres);
                p.setModalGenerationOuvert(true);
              }}
            />
          )}

          <SectionNutritionHebdo nutrition={p.nutrition} />

          <OverlayDialogueAjoutRepas
            dialogueOuvert={p.dialogueOuvert}
            setDialogueOuvert={p.setDialogueOuvert}
            reinitialiserDialogue={p.reinitialiserDialogue}
            dialogueEtape={p.dialogueEtape}
            repasEnCours={p.repasEnCours}
            jours={p.jours}
            datesSemaine={p.datesSemaine}
            ongletDialogue={p.ongletDialogue}
            setOngletDialogue={p.setOngletDialogue}
            rechercheRecette={p.rechercheRecette}
            setRechercheRecette={p.setRechercheRecette}
            suggestions={p.suggestions}
            chargeSuggestions={p.chargeSuggestions}
            suggestionsFiltrees={p.suggestionsFiltrees}
            enAjout={p.enAjout}
            choisirRecette={p.choisirRecette}
            notesRepas={p.notesRepas}
            setNotesRepas={p.setNotesRepas}
            onAjouterTexteLibre={p.ajouterTexteLibre}
            repasIdCree={p.repasIdCree}
            nomRepasAjoute={p.nomRepasAjoute}
            enSuggestionIA={p.enSuggestionIA}
            demanderSuggestionsAccompagnements={p.demanderSuggestionsAccompagnements}
            suggestionsIA={p.suggestionsIA}
            legumesForm={p.legumesForm}
            setLegumesForm={p.setLegumesForm}
            feculentsForm={p.feculentsForm}
            setFeculentsForm={p.setFeculentsForm}
            proteineForm={p.proteineForm}
            setProteineForm={p.setProteineForm}
            laitageForm={p.laitageForm}
            setLaitageForm={p.setLaitageForm}
            dessertForm={p.dessertForm}
            setDessertForm={p.setDessertForm}
            fruitGouter={p.fruitGouter}
            setFruitGouter={p.setFruitGouter}
            gateauGouter={p.gateauGouter}
            setGateauGouter={p.setGateauGouter}
            passerEquilibre={p.passerEquilibre}
            confirmerEquilibre={p.confirmerEquilibre}
          />

          <DialoguesResultatsPlanning
            coursesDialogue={p.coursesDialogue}
            setCoursesDialogue={p.setCoursesDialogue}
            coursesResultat={p.coursesResultat}
            batchDialogue={p.batchDialogue}
            setBatchDialogue={p.setBatchDialogue}
            batchResultat={p.batchResultat}
            choixModePrepa={p.choixModePrepa}
            setChoixModePrepa={p.setChoixModePrepa}
            enGenerationBatch={p.enGenerationBatch}
            genererBatch={p.genererBatch}
          />
        </TabsContent>
      </Tabs>

      <OverlayModalGenerationPlanning
        ouvert={p.modalGenerationOuvert}
        setModalGenerationOuvert={p.setModalGenerationOuvert}
        setModalGenerationInitialPlats={p.setModalGenerationInitialPlats}
        enGeneration={p.enGeneration}
        nbPersonnesInitial={p.nbPersonnes}
        dateDebut={p.dateDebut}
        modalGenerationInitialPlats={p.modalGenerationInitialPlats}
        repasActuelsSemaine={p.repasActuelsSemaine}
        lancerGenerationIA={p.lancerGenerationIA}
      />
    </div>
  );
}