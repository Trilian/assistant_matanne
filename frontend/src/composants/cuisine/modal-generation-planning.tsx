"use client";

import { useState, useCallback, useEffect } from "react";
import { X, Plus, Loader2, Sparkles, Refrigerator, ChevronDown } from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Switch } from "@/composants/ui/switch";
import { listerInventaire } from "@/bibliotheque/api/inventaire";
import {
  obtenirPreferencesPlanning,
  sauvegarderPreferencesPlanning,
} from "@/bibliotheque/api/preferences";
import type { GenererPlanningParams } from "@/types/planning";
import type { ObjetDonnees } from "@/types/commun";

interface CuisineOption {
  id: string;
  label: string;
  emoji: string;
  sousOptions?: { id: string; label: string }[];
}

const CUISINES_DISPONIBLES: CuisineOption[] = [
  { id: "français", label: "🇫🇷 Français", emoji: "🇫🇷" },
  {
    id: "régional français",
    label: "🏡 Régional français",
    emoji: "🏡",
    sousOptions: [
      { id: "breton", label: "Breton" },
      { id: "basque", label: "Basque" },
      { id: "alsacien", label: "Alsacien" },
      { id: "savoyard", label: "Savoyard" },
      { id: "provençal", label: "Provençal" },
    ],
  },
  { id: "italien", label: "🇮🇹 Italien", emoji: "🇮🇹" },
  { id: "japonais", label: "🇯🇵 Japonais", emoji: "🇯🇵" },
  { id: "chinois", label: "🇨🇳 Chinois", emoji: "🇨🇳" },
  { id: "mexicain", label: "🇲🇽 Mexicain", emoji: "🇲🇽" },
  { id: "espagnol", label: "🇪🇸 Espagnol", emoji: "🇪🇸" },
  { id: "américain", label: "🇺🇸 Américain", emoji: "🇺🇸" },
];

interface Props {
  ouvert: boolean;
  onFermer: () => void;
  onGenerer: (params: GenererPlanningParams) => void;
  enGeneration: boolean;
  nbPersonnesInitial?: number;
  dateDebut?: string;
  preferences?: ObjetDonnees;
  /** Plats pré-sélectionnés depuis l'analyse IA (fusionnés avec les préférences sauvegardées) */
  initialPlats?: string[];
  /** Repas déjà planifiés cette semaine — cliquables pour les verrouiller dans la prochaine génération */
  repasActuels?: string[];
}

export function ModalGenerationPlanning({
  ouvert,
  onFermer,
  onGenerer,
  enGeneration,
  nbPersonnesInitial = 2,
  dateDebut,
  preferences,
  initialPlats,
  repasActuels,
}: Props) {
  const [nbPersonnes, setNbPersonnes] = useState(nbPersonnesInitial);
  const [legumes, setLegumes] = useState<string[]>([]);
  const [feculents, setFeculents] = useState<string[]>([]);
  const [plats, setPlats] = useState<string[]>([]);
  const [ingredientsInterdits, setIngredientsInterdits] = useState<string[]>([]);
  const [autoriserRestes, setAutoriserRestes] = useState(true);
  const [cuisinesSouhaitees, setCuisinesSouhaitees] = useState<string[]>([]);
  const [afficherAvance, setAfficherAvance] = useState(false);
  const [inputLegume, setInputLegume] = useState("");
  const [inputFeculent, setInputFeculent] = useState("");
  const [inputPlat, setInputPlat] = useState("");
  const [inputInterdit, setInputInterdit] = useState("");
  const [chargementInventaire, setChargementInventaire] = useState(false);
  const [legumesSuggeres, setLegumesSuggeres] = useState<string[]>([]);
  const [inventaireCharge, setInventaireCharge] = useState(false);

  // Chargement des préférences sauvegardées à l'ouverture du modal
  useEffect(() => {
    if (!ouvert) return;
    obtenirPreferencesPlanning()
      .then((d) => {
        const platsSauvegardes = d.plats_souhaites ?? [];
        // Fusionner les plats initiaux (conseils IA) avec les préférences sauvegardées
        const platsInitiaux = initialPlats ?? [];
        const platsFusionnes = [
          ...platsSauvegardes,
          ...platsInitiaux.filter((p) => !platsSauvegardes.includes(p)),
        ];
        setLegumes(d.legumes_souhaites ?? []);
        setFeculents(d.feculents_souhaites ?? []);
        setPlats(platsFusionnes);
        setIngredientsInterdits(d.ingredients_interdits ?? []);
        setAutoriserRestes(d.autoriser_restes ?? true);
        setNbPersonnes(d.nb_personnes ?? nbPersonnesInitial);
        setCuisinesSouhaitees(d.cuisines_souhaitees ?? []);
        // Ouvrir le panneau avancé si l'utilisateur a des préférences avancées sauvegardées
        if ((d.legumes_souhaites?.length ?? 0) > 0 || (d.feculents_souhaites?.length ?? 0) > 0 || (d.ingredients_interdits?.length ?? 0) > 0) {
          setAfficherAvance(true);
        }
      })
      .catch(() => {
        // silencieux — utiliser initialPlats seuls si les préférences échouent
        if (initialPlats?.length) setPlats(initialPlats);
      });
  }, [ouvert]); // eslint-disable-line react-hooks/exhaustive-deps

  const chargerDepuisInventaire = useCallback(async () => {
    if (inventaireCharge) return;
    setChargementInventaire(true);
    try {
      const articles = await listerInventaire();
      const legumesCat = articles
        .filter(
          (a) =>
            a.categorie?.toLowerCase().includes("légume") ||
            a.categorie?.toLowerCase().includes("legume") ||
            a.categorie?.toLowerCase().includes("fruit") ||
            a.categorie?.toLowerCase().includes("frais")
        )
        .map((a) => a.nom)
        .filter((nom, i, arr) => arr.indexOf(nom) === i); // déduplique
      setLegumesSuggeres(legumesCat);
      setInventaireCharge(true);
    } catch {
      // silencieux — l'utilisateur peut saisir manuellement
    } finally {
      setChargementInventaire(false);
    }
  }, [inventaireCharge]);

  const ajouterLegume = useCallback(
    (nom: string) => {
      const val = nom.trim();
      if (val && !legumes.includes(val)) {
        setLegumes((prev) => [...prev, val]);
      }
      setInputLegume("");
    },
    [legumes]
  );

  const retirerLegume = useCallback((nom: string) => {
    setLegumes((prev) => prev.filter((l) => l !== nom));
    setLegumesSuggeres((prev) => prev); // garde les suggestions disponibles pour re-sélection
  }, []);

  const ajouterFeculent = useCallback(
    (nom: string) => {
      const val = nom.trim();
      if (val && !feculents.includes(val)) {
        setFeculents((prev) => [...prev, val]);
      }
      setInputFeculent("");
    },
    [feculents]
  );

  const retirerFeculent = useCallback((nom: string) => {
    setFeculents((prev) => prev.filter((f) => f !== nom));
  }, []);

  const ajouterPlat = useCallback(
    (nom: string) => {
      const val = nom.trim();
      if (val && !plats.includes(val)) {
        setPlats((prev) => [...prev, val]);
      }
      setInputPlat("");
    },
    [plats]
  );

  const retirerPlat = useCallback((nom: string) => {
    setPlats((prev) => prev.filter((p) => p !== nom));
  }, []);

  const ajouterInterdit = useCallback(
    (nom: string) => {
      const val = nom.trim();
      if (val && !ingredientsInterdits.includes(val)) {
        setIngredientsInterdits((prev) => [...prev, val]);
      }
      setInputInterdit("");
    },
    [ingredientsInterdits]
  );

  const retirerInterdit = useCallback((nom: string) => {
    setIngredientsInterdits((prev) => prev.filter((i) => i !== nom));
  }, []);

  const basculerCuisine = useCallback((id: string) => {
    const cuisine = CUISINES_DISPONIBLES.find((c) => c.id === id);
    if (cuisine?.sousOptions) {
      // Toggle parent = montre/cache les sous-options
      // Si on désactive le parent, retirer aussi toutes les sous-options
      setCuisinesSouhaitees((prev) => {
        const sousIds = cuisine.sousOptions!.map((s) => s.id);
        if (prev.includes(id)) {
          return prev.filter((c) => c !== id && !sousIds.includes(c));
        }
        return [...prev, id];
      });
    } else {
      setCuisinesSouhaitees((prev) =>
        prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
      );
    }
  }, []);

  const basculerSousRegion = useCallback((parentId: string, sousId: string) => {
    setCuisinesSouhaitees((prev) => {
      const next = prev.includes(sousId)
        ? prev.filter((c) => c !== sousId)
        : [...prev, sousId];
      // Si plus aucune sous-région sélectionnée mais parent actif, on garde le parent
      // comme fallback pour que l'IA sache qu'on veut du régional
      return next;
    });
  }, []);

  const handleGenerer = () => {
    // Sauvegarde silencieuse des paramètres courants en DB
    sauvegarderPreferencesPlanning({
      legumes_souhaites: legumes,
      feculents_souhaites: feculents,
      plats_souhaites: plats,
      ingredients_interdits: ingredientsInterdits,
      autoriser_restes: autoriserRestes,
      nb_personnes: nbPersonnes,
      cuisines_souhaitees: cuisinesSouhaitees,
    }).catch(() => {
      // silencieux — la génération continue même si la sauvegarde échoue
    });
    onGenerer({
      date_debut: dateDebut,
      nb_personnes: nbPersonnes,
      preferences: preferences,
      legumes_souhaites: legumes,
      feculents_souhaites: feculents,
      plats_souhaites: plats,
      ingredients_interdits: ingredientsInterdits,
      autoriser_restes: autoriserRestes,
      cuisines_souhaitees: cuisinesSouhaitees,
    });
  };

  return (
    <Dialog open={ouvert} onOpenChange={(o) => !o && onFermer()}>
      <DialogContent className="sm:max-w-[500px] max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Générer le planning de la semaine
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-5 py-2">

          {/* ═══════════════════════════════════════════════ */}
          {/* SECTION ESSENTIELLE — toujours visible         */}
          {/* ═══════════════════════════════════════════════ */}

          {/* Nombre de personnes */}
          <div className="space-y-2">
            <Label>Nombre de personnes</Label>
            <div className="flex items-center gap-3">
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setNbPersonnes((n) => Math.max(1, n - 1))}
                disabled={nbPersonnes <= 1}
              >
                −
              </Button>
              <span className="w-8 text-center font-medium tabular-nums">{nbPersonnes}</span>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setNbPersonnes((n) => Math.min(20, n + 1))}
                disabled={nbPersonnes >= 20}
              >
                +
              </Button>
            </div>
          </div>

          {/* Repas à conserver de la semaine actuelle */}
          {repasActuels && repasActuels.length > 0 && (
            <div className="space-y-2">
              <Label>
                Conserver des repas de cette semaine{" "}
                <span className="text-muted-foreground font-normal text-xs">(cliquez pour verrouiller)</span>
              </Label>
              <div className="flex flex-wrap gap-1.5">
                {repasActuels.map((nom) => {
                  const estSelectionne = plats.includes(nom);
                  return (
                    <button
                      key={nom}
                      type="button"
                      onClick={() => estSelectionne ? retirerPlat(nom) : ajouterPlat(nom)}
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium border transition-colors ${
                        estSelectionne
                          ? "bg-emerald-100 border-emerald-400 text-emerald-800 dark:bg-emerald-900/40 dark:border-emerald-600 dark:text-emerald-200"
                          : "border-dashed border-muted-foreground/40 text-muted-foreground hover:border-emerald-400 hover:text-emerald-700 dark:hover:border-emerald-500 dark:hover:text-emerald-300"
                      }`}
                    >
                      {estSelectionne ? "✓ " : "+ "}{nom}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Plats souhaités */}
          <div className="space-y-2">
            <Label>
              Plats à inclure{" "}
              <span className="text-muted-foreground font-normal text-xs">(forte préférence)</span>
            </Label>

            {plats.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {plats.map((p) => (
                  <span
                    key={p}
                    className="inline-flex items-center gap-1 rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium"
                  >
                    {p}
                    <button
                      type="button"
                      onClick={() => retirerPlat(p)}
                      aria-label={`Retirer ${p}`}
                      className="rounded-full hover:bg-muted p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <Input
                placeholder="Ex: lasagnes, tarte aux poireaux…"
                value={inputPlat}
                onChange={(e) => setInputPlat(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    ajouterPlat(inputPlat);
                  }
                }}
                className="h-8 text-sm"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="h-8 w-8 shrink-0"
                onClick={() => ajouterPlat(inputPlat)}
                disabled={!inputPlat.trim()}
              >
                <Plus className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>

          {/* 🌍 Cuisines du monde */}
          <div className="space-y-2">
            <Label>
              Cuisines du monde{" "}
              <span className="text-muted-foreground font-normal text-xs">(2-3 repas d&apos;inspiration)</span>
            </Label>
            <div className="space-y-2">
              <div className="flex flex-wrap gap-1.5">
                {CUISINES_DISPONIBLES.map((c) => {
                  const estActive = cuisinesSouhaitees.includes(c.id);
                  return (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => basculerCuisine(c.id)}
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium border transition-colors ${
                        estActive
                          ? "bg-primary/10 border-primary text-primary"
                          : "border-dashed border-muted-foreground/40 text-muted-foreground hover:border-primary hover:text-primary"
                      }`}
                    >
                      {c.label}
                    </button>
                  );
                })}
              </div>
              {/* Sous-régions dépliables pour Régional français */}
              {CUISINES_DISPONIBLES.filter((c) => c.sousOptions && cuisinesSouhaitees.includes(c.id)).map((c) => (
                <div key={`sub-${c.id}`} className="flex flex-wrap gap-1.5 ml-3 pl-3 border-l-2 border-primary/20">
                  {c.sousOptions!.map((s) => {
                    const estActive = cuisinesSouhaitees.includes(s.id);
                    return (
                      <button
                        key={s.id}
                        type="button"
                        onClick={() => basculerSousRegion(c.id, s.id)}
                        className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium border transition-colors ${
                          estActive
                            ? "bg-primary/10 border-primary text-primary"
                            : "border-dashed border-muted-foreground/40 text-muted-foreground hover:border-primary hover:text-primary"
                        }`}
                      >
                        {s.label}
                      </button>
                    );
                  })}
                </div>
              ))}
            </div>
            {cuisinesSouhaitees.length === 0 && (
              <p className="text-xs text-muted-foreground">
                Aucune sélection = variété libre (l&apos;IA explore toutes les cuisines)
              </p>
            )}
          </div>

          {/* Restes réchauffés */}
          <div className="flex items-center justify-between gap-3 rounded-lg border px-3 py-2.5">
            <div className="space-y-0.5">
              <Label className="text-sm">Proposer des restes réchauffés</Label>
              <p className="text-xs text-muted-foreground">
                Ex&nbsp;: poulet rôti du soir → réchauffé le midi suivant
              </p>
            </div>
            <Switch checked={autoriserRestes} onCheckedChange={setAutoriserRestes} />
          </div>

          {/* ═══════════════════════════════════════════════ */}
          {/* SECTION AVANCÉE — pliable                      */}
          {/* ═══════════════════════════════════════════════ */}

          <button
            type="button"
            onClick={() => setAfficherAvance((v) => !v)}
            className="flex items-center gap-1.5 w-full text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
          >
            <ChevronDown className={`h-3.5 w-3.5 transition-transform ${afficherAvance ? "rotate-180" : ""}`} />
            Options avancées
            {(legumes.length > 0 || feculents.length > 0 || ingredientsInterdits.length > 0) && (
              <span className="ml-auto text-[10px] bg-muted px-1.5 py-0.5 rounded-full">
                {legumes.length + feculents.length + ingredientsInterdits.length} critère{legumes.length + feculents.length + ingredientsInterdits.length > 1 ? "s" : ""}
              </span>
            )}
          </button>

          {afficherAvance && (
            <div className="space-y-5 border-t pt-4">

              {/* Légumes souhaités */}
              <div className="space-y-2">
                <Label>
                  Légumes à privilégier{" "}
                  <span className="text-muted-foreground font-normal text-xs">(forte préférence)</span>
                </Label>

                {legumes.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {legumes.map((l) => (
                      <span
                        key={l}
                        className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                      >
                        {l}
                        <button
                          type="button"
                          onClick={() => retirerLegume(l)}
                          aria-label={`Retirer ${l}`}
                          className="rounded-full hover:bg-primary/20 p-0.5"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {!inventaireCharge ? (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs gap-1"
                    onClick={chargerDepuisInventaire}
                    disabled={chargementInventaire}
                  >
                    {chargementInventaire ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <Refrigerator className="h-3 w-3" />
                    )}
                    Depuis mon inventaire
                  </Button>
                ) : legumesSuggeres.length > 0 ? (
                  <div className="flex flex-wrap gap-1">
                    {legumesSuggeres
                      .filter((l) => !legumes.includes(l))
                      .map((l) => (
                        <button
                          key={l}
                          type="button"
                          onClick={() => ajouterLegume(l)}
                          className="inline-flex items-center gap-1 rounded-full border border-dashed border-muted-foreground/40 px-2.5 py-0.5 text-xs text-muted-foreground hover:border-primary hover:text-primary transition-colors"
                        >
                          + {l}
                        </button>
                      ))}
                    {legumesSuggeres.filter((l) => !legumes.includes(l)).length === 0 && (
                      <span className="text-xs text-muted-foreground">Tous les légumes ajoutés ✓</span>
                    )}
                  </div>
                ) : (
                  <span className="text-xs text-muted-foreground">
                    Aucun légume trouvé dans l&apos;inventaire
                  </span>
                )}

                <div className="flex gap-2">
                  <Input
                    placeholder="Ex: courgettes, brocoli…"
                    value={inputLegume}
                    onChange={(e) => setInputLegume(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        ajouterLegume(inputLegume);
                      }
                    }}
                    className="h-8 text-sm"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 shrink-0"
                    onClick={() => ajouterLegume(inputLegume)}
                    disabled={!inputLegume.trim()}
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* Féculents souhaités */}
              <div className="space-y-2">
                <Label>
                  Féculents à privilégier{" "}
                  <span className="text-muted-foreground font-normal text-xs">(forte préférence)</span>
                </Label>

                {feculents.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {feculents.map((f) => (
                      <span
                        key={f}
                        className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                      >
                        🍚 {f}
                        <button
                          type="button"
                          onClick={() => retirerFeculent(f)}
                          aria-label={`Retirer ${f}`}
                          className="rounded-full hover:bg-primary/20 p-0.5"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  <Input
                    placeholder="Ex: pommes de terre vapeur, riz basmati…"
                    value={inputFeculent}
                    onChange={(e) => setInputFeculent(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        ajouterFeculent(inputFeculent);
                      }
                    }}
                    className="h-8 text-sm"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 shrink-0"
                    onClick={() => ajouterFeculent(inputFeculent)}
                    disabled={!inputFeculent.trim()}
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* Ingrédients interdits */}
              <div className="space-y-2">
                <Label>
                  Ingrédients à exclure{" "}
                  <span className="text-muted-foreground font-normal text-xs">
                    (pour cette génération uniquement)
                  </span>
                </Label>

                {ingredientsInterdits.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {ingredientsInterdits.map((i) => (
                      <span
                        key={i}
                        className="inline-flex items-center gap-1 rounded-full bg-destructive/10 px-2.5 py-0.5 text-xs font-medium text-destructive"
                      >
                        🚫 {i}
                        <button
                          type="button"
                          onClick={() => retirerInterdit(i)}
                          aria-label={`Retirer ${i}`}
                          className="rounded-full hover:bg-destructive/20 p-0.5"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  <Input
                    placeholder="Ex: concombre, champignons…"
                    value={inputInterdit}
                    onChange={(e) => setInputInterdit(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        e.preventDefault();
                        ajouterInterdit(inputInterdit);
                      }
                    }}
                    className="h-8 text-sm"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 shrink-0"
                    onClick={() => ajouterInterdit(inputInterdit)}
                    disabled={!inputInterdit.trim()}
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

            </div>
          )}
        </div>

        <DialogFooter>
          <Button type="button" variant="ghost" onClick={onFermer} disabled={enGeneration}>
            Annuler
          </Button>
          <Button type="button" onClick={handleGenerer} disabled={enGeneration}>
            {enGeneration ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Génération…
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Générer
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
