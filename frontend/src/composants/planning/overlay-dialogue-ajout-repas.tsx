'use client'

import { ResponsiveOverlay } from "@/composants/planning/responsive-overlay";
import { DialogueAjoutRepasPlanning } from "@/composants/planning/dialogue-ajout-repas-planning";
import {
  TYPES_REPAS,
} from "@/composants/planning/grille-planning-hebdo";
import type {
  SuggestionAccompagnement,
  SuggestionRecettePlanning,
  TypeRepas,
} from "@/types/planning";

type RepasEnCours = { date: string; type_repas: TypeRepas };

interface OverlayDialogueAjoutRepasProps {
  dialogueOuvert: boolean;
  setDialogueOuvert: (open: boolean) => void;
  reinitialiserDialogue: () => void;
  dialogueEtape: "choisir" | "equilibre";
  repasEnCours: RepasEnCours | null;
  jours: string[];
  datesSemaine: string[];
  ongletDialogue: "suggestions" | "libre";
  setOngletDialogue: (v: "suggestions" | "libre") => void;
  rechercheRecette: string;
  setRechercheRecette: (v: string) => void;
  suggestions?: SuggestionRecettePlanning[];
  chargeSuggestions: boolean;
  suggestionsFiltrees: SuggestionRecettePlanning[];
  enAjout: boolean;
  choisirRecette: (recette: SuggestionRecettePlanning) => void;
  notesRepas: string;
  setNotesRepas: (v: string) => void;
  onAjouterTexteLibre: () => void;
  repasIdCree: number | null;
  nomRepasAjoute: string;
  enSuggestionIA: boolean;
  demanderSuggestionsAccompagnements: () => void | Promise<void>;
  suggestionsIA: SuggestionAccompagnement | null;
  legumesForm: string;
  setLegumesForm: (v: string) => void;
  feculentsForm: string;
  setFeculentsForm: (v: string) => void;
  proteineForm: string;
  setProteineForm: (v: string) => void;
  laitageForm: string;
  setLaitageForm: (v: string) => void;
  dessertForm: string;
  setDessertForm: (v: string) => void;
  fruitGouter: string;
  setFruitGouter: (v: string) => void;
  gateauGouter: string;
  setGateauGouter: (v: string) => void;
  passerEquilibre: () => void;
  confirmerEquilibre: () => void | Promise<void>;
}

export function OverlayDialogueAjoutRepas({
  dialogueOuvert,
  setDialogueOuvert,
  reinitialiserDialogue,
  dialogueEtape,
  repasEnCours,
  jours,
  datesSemaine,
  ongletDialogue,
  setOngletDialogue,
  rechercheRecette,
  setRechercheRecette,
  suggestions,
  chargeSuggestions,
  suggestionsFiltrees,
  enAjout,
  choisirRecette,
  notesRepas,
  setNotesRepas,
  onAjouterTexteLibre,
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
}: OverlayDialogueAjoutRepasProps) {
  return (
    <ResponsiveOverlay
      open={dialogueOuvert}
      onOpenChange={(open) => {
        setDialogueOuvert(open);
        if (!open) reinitialiserDialogue();
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
        onAjouterTexteLibre={onAjouterTexteLibre}
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
  );
}
