import { useCallback, useMemo, useState } from "react";
import type {
  SuggestionAccompagnement,
  SuggestionRecettePlanning,
  TypeRepas,
} from "@/types/planning";

type RepasEnCours = {
  date: string;
  type_repas: TypeRepas;
};

export function utiliserPlanningDialogue(suggestions?: SuggestionRecettePlanning[]) {
  const [dialogueOuvert, setDialogueOuvert] = useState(false);
  const [repasEnCours, setRepasEnCours] = useState<RepasEnCours | null>(null);
  const [notesRepas, setNotesRepas] = useState("");
  const [ongletDialogue, setOngletDialogue] = useState<"suggestions" | "libre">("suggestions");
  const [rechercheRecette, setRechercheRecette] = useState("");
  const [repasIdCree, setRepasIdCree] = useState<number | null>(null);
  const [dialogueEtape, setDialogueEtape] = useState<"choisir" | "equilibre">("choisir");
  const [legumesForm, setLegumesForm] = useState("");
  const [feculentsForm, setFeculentsForm] = useState("");
  const [proteineForm, setProteineForm] = useState("");
  const [laitageForm, setLaitageForm] = useState("");
  const [dessertForm, setDessertForm] = useState("");
  const [fruitGouter, setFruitGouter] = useState("");
  const [gateauGouter, setGateauGouter] = useState("");
  const [nomRepasAjoute, setNomRepasAjoute] = useState("");
  const [suggestionsIA, setSuggestionsIA] = useState<SuggestionAccompagnement | null>(null);
  const [enSuggestionIA, setEnSuggestionIA] = useState(false);

  const reinitialiserDialogue = useCallback(() => {
    setRepasEnCours(null);
    setNotesRepas("");
    setRechercheRecette("");
    setOngletDialogue("suggestions");
    setRepasIdCree(null);
    setDialogueEtape("choisir");
    setLegumesForm("");
    setFeculentsForm("");
    setProteineForm("");
    setLaitageForm("");
    setDessertForm("");
    setFruitGouter("");
    setGateauGouter("");
    setNomRepasAjoute("");
    setSuggestionsIA(null);
  }, []);

  const ouvrirDialogue = useCallback(
    (date: string, type: TypeRepas) => {
      reinitialiserDialogue();
      setRepasEnCours({ date, type_repas: type });
      setDialogueOuvert(true);
    },
    [reinitialiserDialogue]
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

  return {
    dialogueOuvert,
    setDialogueOuvert,
    repasEnCours,
    setRepasEnCours,
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
    suggestionsFiltrees,
    ouvrirDialogue,
    reinitialiserDialogue,
  };
}
