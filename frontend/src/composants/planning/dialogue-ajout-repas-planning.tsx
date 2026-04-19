"use client";

import { Clock, Loader2, Plus, Search } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { ConvertisseurInline } from "@/composants/cuisine/convertisseur-inline";
import type {
  SuggestionAccompagnement,
  SuggestionRecettePlanning,
  TypeRepas,
} from "@/types/planning";

type RepasEnCours = {
  date: string;
  type_repas: TypeRepas;
};

type TypeRepasOption = {
  valeur: TypeRepas;
  label: string;
  emoji: string;
};

type DialogueAjoutRepasPlanningProps = {
  repasEnCours: RepasEnCours | null;
  jours: string[];
  datesSemaine: string[];
  typesRepas: TypeRepasOption[];
  dialogueEtape: "choisir" | "equilibre";
  ongletDialogue: "suggestions" | "libre";
  setOngletDialogue: (valeur: "suggestions" | "libre") => void;
  rechercheRecette: string;
  setRechercheRecette: (valeur: string) => void;
  suggestions?: SuggestionRecettePlanning[];
  chargeSuggestions: boolean;
  suggestionsFiltrees: SuggestionRecettePlanning[];
  enAjout: boolean;
  choisirRecette: (recette: SuggestionRecettePlanning) => void;
  notesRepas: string;
  setNotesRepas: (valeur: string) => void;
  onAnnulerAjout: () => void;
  onAjouterTexteLibre: () => void;
  repasIdCree: number | null;
  nomRepasAjoute: string;
  enSuggestionIA: boolean;
  onDemanderSuggestions: () => void | Promise<void>;
  suggestionsIA: SuggestionAccompagnement | null;
  legumesForm: string;
  setLegumesForm: (valeur: string) => void;
  feculentsForm: string;
  setFeculentsForm: (valeur: string) => void;
  proteineForm: string;
  setProteineForm: (valeur: string) => void;
  laitageForm: string;
  setLaitageForm: (valeur: string) => void;
  dessertForm: string;
  setDessertForm: (valeur: string) => void;
  fruitGouter: string;
  setFruitGouter: (valeur: string) => void;
  gateauGouter: string;
  setGateauGouter: (valeur: string) => void;
  onPasserEquilibre: () => void;
  onConfirmerEquilibre: () => void | Promise<void>;
};

const MOTS_FECULENTS_PLAT = [
  "gratin",
  "lasagne",
  "lasagnes",
  "risotto",
  "tartiflette",
  "purée",
  "puree",
  "pâtes",
  "pasta",
  "gnocchi",
  "ravioli",
  "raviolis",
  "pizza",
  "quiche",
  "hachis parmentier",
  "carbonara",
  "bolognaise",
  "polenta",
  "macaroni",
  "semoule",
  "tarte salée",
  "tourte",
  "flamiche",
];

const PROTEINES_RAPIDES = [
  "Entrecôte",
  "Côtelettes d'agneau",
  "Escalope de veau",
  "Filet mignon",
  "Saucisses",
  "Merguez",
  "Poulet rôti",
  "Blanc de poulet",
];

export function DialogueAjoutRepasPlanning({
  repasEnCours,
  jours,
  datesSemaine,
  typesRepas,
  dialogueEtape,
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
  onAnnulerAjout,
  onAjouterTexteLibre,
  repasIdCree,
  nomRepasAjoute,
  enSuggestionIA,
  onDemanderSuggestions,
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
  onPasserEquilibre,
  onConfirmerEquilibre,
}: DialogueAjoutRepasPlanningProps) {
  const estPlatFeculent = MOTS_FECULENTS_PLAT.some((mot) =>
    nomRepasAjoute.toLowerCase().includes(mot)
  );

  return (
    <>
      {repasEnCours && (
        <p className="text-sm text-muted-foreground -mt-2">
          {jours[datesSemaine.indexOf(repasEnCours.date)]}{" "}
          {new Date(repasEnCours.date).toLocaleDateString("fr-FR", {
            day: "numeric",
            month: "long",
          })}{" "}
          — {typesRepas.find((t) => t.valeur === repasEnCours.type_repas)?.emoji}{" "}
          {typesRepas.find((t) => t.valeur === repasEnCours.type_repas)?.label}
        </p>
      )}

      {dialogueEtape === "choisir" && (
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
                Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-14 w-full" />)
              ) : suggestionsFiltrees.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-6">Aucune recette trouvée</p>
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

          <TabsContent value="libre" className="space-y-4 mt-3">
            <p className="text-xs text-muted-foreground rounded-md border border-dashed px-3 py-2">
              💡 Pour les plats complexes (gratin, lasagnes, risotto…), préférez l'onglet <span className="font-medium">Recettes</span> afin de lier une fiche recette et activer le suivi nutritionnel complet.
            </p>
            <Input value={notesRepas} onChange={(e) => setNotesRepas(e.target.value)} placeholder="Ex: Quiche lorraine" />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={onAnnulerAjout}>
                Annuler
              </Button>
              <Button disabled={enAjout || !notesRepas.trim()} onClick={onAjouterTexteLibre}>
                {enAjout && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Ajouter
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      )}

      {dialogueEtape === "equilibre" && repasIdCree != null && repasEnCours && (
        <div className="space-y-4 mt-2">
          {repasEnCours.type_repas === "gouter" ? (
            <>
              <p className="text-xs text-muted-foreground">Complétez le goûter (PNNS4 : laitage + fruit + gâteau sain).</p>
              <div className="space-y-2">
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🥛 Laitage</label>
                  <Input value={laitageForm} onChange={(e) => setLaitageForm(e.target.value)} placeholder="Ex: Yaourt nature, fromage blanc…" className="mt-1" />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🍎 Fruit</label>
                  <Input value={fruitGouter} onChange={(e) => setFruitGouter(e.target.value)} placeholder="Ex: Pomme, Compote poire…" className="mt-1" />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🍪 Gâteau / biscuit sain</label>
                  <Input value={gateauGouter} onChange={(e) => setGateauGouter(e.target.value)} placeholder="Ex: Cake maison, biscuit complet…" className="mt-1" />
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">Équilibrez l'assiette (PNNS4 : ≥½ légumes, ¼ féculents, ¼ protéines).</p>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={enSuggestionIA}
                  onClick={async () => {
                    try {
                      await onDemanderSuggestions();
                    } catch {
                      toast.error("Impossible de générer des suggestions");
                    }
                  }}
                >
                  {enSuggestionIA ? <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" /> : <span className="mr-1.5">✨</span>}
                  Suggérer
                </Button>
              </div>

              {estPlatFeculent && (
                <div className="rounded-md border border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-950/30 p-3 space-y-2">
                  <p className="text-xs font-semibold text-amber-800 dark:text-amber-200">🥩 Plat féculent détecté — ajoutez une protéine</p>
                  <p className="text-xs text-amber-700 dark:text-amber-300">
                    <span className="font-medium">{nomRepasAjoute}</span> n'apporte pas de protéine. Associez une viande ou une autre source.
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {PROTEINES_RAPIDES.map((p) => (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setProteineForm(p)}
                        className={`rounded-full border px-2.5 py-0.5 text-[11px] transition-colors ${
                          proteineForm === p
                            ? "border-amber-500 bg-amber-100 font-semibold text-amber-800 dark:bg-amber-900/50 dark:text-amber-200"
                            : "border-border bg-background hover:bg-accent text-foreground"
                        }`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                  <Input value={proteineForm} onChange={(e) => setProteineForm(e.target.value)} placeholder="Ou saisissez une autre protéine…" className="mt-1 border-amber-300 focus:border-amber-500" />
                </div>
              )}

              {suggestionsIA && (
                <div className="rounded-md border bg-muted/30 p-3 space-y-2 text-xs">
                  {suggestionsIA.legumes.length > 0 && (
                    <div>
                      <span className="font-medium text-muted-foreground">🥦 Légumes :</span>{" "}
                      <span className="flex flex-wrap gap-1 mt-1">
                        {suggestionsIA.legumes.map((s) => (
                          <button key={s} onClick={() => setLegumesForm(s)} className="rounded bg-background border px-2 py-0.5 hover:bg-accent transition-colors">
                            {s}
                          </button>
                        ))}
                      </span>
                    </div>
                  )}
                  {suggestionsIA.feculents.length > 0 && (
                    <div>
                      <span className="font-medium text-muted-foreground">🍚 Féculents :</span>{" "}
                      <span className="flex flex-wrap gap-1 mt-1">
                        {suggestionsIA.feculents.map((s) => (
                          <button key={s} onClick={() => setFeculentsForm(s)} className="rounded bg-background border px-2 py-0.5 hover:bg-accent transition-colors">
                            {s}
                          </button>
                        ))}
                      </span>
                    </div>
                  )}
                  {suggestionsIA.proteines.length > 0 && (
                    <div>
                      <span className="font-medium text-muted-foreground">🥩 Protéines :</span>{" "}
                      <span className="flex flex-wrap gap-1 mt-1">
                        {suggestionsIA.proteines.map((s) => (
                          <button key={s} onClick={() => setProteineForm(s)} className="rounded bg-background border px-2 py-0.5 hover:bg-accent transition-colors">
                            {s}
                          </button>
                        ))}
                      </span>
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-2">
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🥦 Légumes</label>
                  <Input value={legumesForm} onChange={(e) => setLegumesForm(e.target.value)} placeholder="Ex: Haricots verts, Courgettes sautées…" className="mt-1" />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🍚 Féculents</label>
                  <Input value={feculentsForm} onChange={(e) => setFeculentsForm(e.target.value)} placeholder="Ex: Riz vapeur, Pommes de terre…" className="mt-1" />
                </div>
                {!estPlatFeculent && (
                  <div>
                    <label className="text-xs font-medium text-muted-foreground">🥩 Protéine accompagnement</label>
                    <Input value={proteineForm} onChange={(e) => setProteineForm(e.target.value)} placeholder="Ex: Filet de poulet, Œufs durs… (si plat principal = féculent)" className="mt-1" />
                  </div>
                )}
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🥛 Laitage</label>
                  <Input value={laitageForm} onChange={(e) => setLaitageForm(e.target.value)} placeholder="Ex: Yaourt nature, Fromage blanc…" className="mt-1" />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">🍮 Dessert / Fruit</label>
                  <Input value={dessertForm} onChange={(e) => setDessertForm(e.target.value)} placeholder="Ex: Compote, Fruit frais, Tarte aux pommes…" className="mt-1" />
                </div>
              </div>
            </>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={onPasserEquilibre}>
              Passer
            </Button>
            <Button size="sm" disabled={enAjout} onClick={onConfirmerEquilibre}>
              Confirmer
            </Button>
          </div>
        </div>
      )}
    </>
  );
}
