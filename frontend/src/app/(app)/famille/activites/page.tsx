// ═══════════════════════════════════════════════════════════
// Activités familiales
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useEffect } from "react";
import {
  Plus,
  CalendarHeart,
  MapPin,
  Clock,
  Users,
  Loader2,
  Check,
  Filter,
  Sparkles,
  CloudRain,
  Sun,
  Cloud,
  Home,
  TreePine,
  Euro,
  Timer,
  Dumbbell,
  Puzzle,
  Palette,
  BookOpen,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerActivites,
  creerActivite,
  obtenirSuggestionsActivites,
  obtenirSuggestionsActivitesAuto,
} from "@/bibliotheque/api/famille";
import type { SuggestionActivite } from "@/bibliotheque/api/famille";
import type { Activite } from "@/types/famille";
import { toast } from "sonner";

const TYPES_ACTIVITE = [
  "tous",
  "sortie",
  "jeu",
  "sport",
  "culture",
  "repas",
  "visite",
  "autre",
];

export default function PageActivites() {
  const [typeFiltre, setTypeFiltre] = useState("tous");
  const [dialogueCreation, setDialogueCreation] = useState(false);
  const [dialogueSuggestions, setDialogueSuggestions] = useState(false);
  // PHASE C — Auto-prefill states
  const [infoPrefill, setInfoPrefill] = useState<string | null>(null);
  const [prefillDismiss, setPrefillDismiss] = useState(false);
  const [suggestionsIA, setSuggestionsIA] = useState<string>("");
  const [suggestionsStruct, setSuggestionsStruct] = useState<
    Array<{
      titre: string;
      description: string;
      type: string;
      duree_minutes: number;
      lieu: string;
    }>
  >([]);
  const [meteoDetectee, setMeteoDetectee] = useState<string | null>(null);
  const [journeeLibreDetectee, setJourneeLibreDetectee] = useState(false);
  const [typePrefere, setTypePrefere] = useState<string>("mixte");
  const [enChargementIA, setEnChargementIA] = useState(false);
  const [banniereIAVisible, setBanniereIAVisible] = useState(false);

  // Form state
  const [titre, setTitre] = useState("");
  const [type, setType] = useState("sortie");
  const [date, setDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [lieu, setLieu] = useState("");
  const [duree, setDuree] = useState("");
  const [description, setDescription] = useState("");

  const invalider = utiliserInvalidation();

  const { data: activites, isLoading } = utiliserRequete(
    ["famille", "activites", typeFiltre],
    () => listerActivites(typeFiltre !== "tous" ? typeFiltre : undefined)
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (act: Omit<Activite, "id">) => creerActivite(act),
    {
      onSuccess: () => {
        invalider(["famille", "activites"]);
        setDialogueCreation(false);
        setTitre("");
        setLieu("");
        setDuree("");
        setDescription("");
        toast.success("Activité créée");
      },
      onError: () => toast.error("Erreur lors de la création"),
    }
  );

  const genererSuggestionsIA = async () => {
    setEnChargementIA(true);
    try {
      const resultat = await obtenirSuggestionsActivitesAuto({
        type_prefere: typePrefere === "mixte" ? undefined : typePrefere,
      });
      setSuggestionsIA(resultat.suggestions);
      setSuggestionsStruct(resultat.suggestions_struct ?? []);
      setMeteoDetectee(resultat.meteo ?? null);
      setJourneeLibreDetectee(Boolean(resultat.journee_libre));
      toast.success(
        resultat.journee_libre
          ? "Journée libre détectée ! Voici les suggestions"
          : "Suggestions générées avec météo réelle"
      );
    } catch {
      toast.error("Erreur lors de la génération des suggestions");
    } finally {
      setEnChargementIA(false);
    }
  };

  const activitesAVenir = (activites ?? []).filter((a) => !a.est_terminee);
  const activitesPassees = (activites ?? []).filter((a) => a.est_terminee);

  const appliquerSuggestion = (suggestion: {
    titre: string;
    description: string;
    type: string;
    duree_minutes: number;
    lieu: string;
  }) => {
    setTitre(suggestion.titre);
    setType(suggestion.type || "autre");
    setDescription(suggestion.description || "");
    setDuree(String(suggestion.duree_minutes || 60));
    setLieu(suggestion.lieu || "");
    setDialogueSuggestions(false);
    setDialogueCreation(true);
    toast.success("Suggestion injectée dans le formulaire");
  };

  // PHASE C — Auto-prefill à l'ouverture du dialog si suggestions disponibles et contexte détecté
  useEffect(() => {
    if (
      dialogueCreation &&
      !prefillDismiss &&
      suggestionsStruct.length > 0 &&
      (meteoDetectee !== null || journeeLibreDetectee)
    ) {
      appliquerSuggestion(suggestionsStruct[0]);
      const raisons = [meteoDetectee && `météo ${meteoDetectee}`, journeeLibreDetectee && 'journée libre'].filter(Boolean).join(', ');
      setInfoPrefill(raisons);
    }
    if (!dialogueCreation) {
      setPrefillDismiss(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dialogueCreation]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            🎉 Activités
          </h1>
          <p className="text-muted-foreground">
            Activités familiales et sorties
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setDialogueSuggestions(true)}
            disabled={enChargementIA}
          >
            {enChargementIA ? (
              <Loader2 className="mr-1 h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="mr-1 h-4 w-4" />
            )}
            Suggestions IA
          </Button>
          <Button onClick={() => setDialogueCreation(true)}>
            <Plus className="mr-1 h-4 w-4" />
            Nouvelle activité
          </Button>
        </div>
      </div>

      {/* Filtre type */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <Select value={typeFiltre} onValueChange={setTypeFiltre}>
          <SelectTrigger className="w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {TYPES_ACTIVITE.map((t) => (
              <SelectItem key={t} value={t}>
                {t === "tous" ? "Tous les types" : t.charAt(0).toUpperCase() + t.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      ) : !activites?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <CalendarHeart className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucune activité planifiée</p>
            <Button
              variant="outline"
              onClick={() => setDialogueCreation(true)}
            >
              <Plus className="mr-1 h-4 w-4" />
              Planifier une activité
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* À venir */}
          {activitesAVenir.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">À venir</h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {activitesAVenir.map((a) => (
                  <ActiviteCard key={a.id} activite={a} />
                ))}
              </div>
            </div>
          )}

          {/* Passées */}
          {activitesPassees.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold text-muted-foreground">
                Terminées
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 opacity-70">
                {activitesPassees.map((a) => (
                  <ActiviteCard key={a.id} activite={a} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Dialogue création */}
      <Dialog open={dialogueCreation} onOpenChange={setDialogueCreation}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nouvelle activité</DialogTitle>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (!titre.trim()) return;
              creer({
                titre: titre.trim(),
                type,
                date,
                description: description || undefined,
                lieu: lieu || undefined,
                duree_minutes: duree ? Number(duree) : undefined,
                est_terminee: false,
              });
            }}
          >
            {/* PHASE C — Info banner auto-prefill */}
            {infoPrefill && !prefillDismiss && (
              <div className="flex items-center justify-between rounded-md bg-blue-50 dark:bg-blue-950/30 px-3 py-2 text-xs text-blue-700 dark:text-blue-300 mb-3">
                <span>💡 Pré-rempli automatiquement ({infoPrefill})</span>
                <div className="flex gap-2 ml-2 shrink-0">
                  <button 
                    type="button" 
                    className="underline" 
                    onClick={() => setDialogueSuggestions(true)}
                  >
                    Changer
                  </button>
                  <button type="button" onClick={() => setPrefillDismiss(true)}>×</button>
                </div>
              </div>
            )}
            {banniereIAVisible && (
              <div className="flex items-center gap-2 rounded-md bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 px-3 py-2 text-xs text-amber-800 dark:text-amber-200 mb-3">
                <Sparkles className="h-3.5 w-3.5 shrink-0 text-amber-500" />
                <span>Pré-rempli selon la météo / journée libre</span>
                <button onClick={() => setBanniereIAVisible(false)} className="ml-auto text-amber-600 hover:text-amber-800 dark:text-amber-400">✕</button>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="act-titre">Titre *</Label>
              <Input
                id="act-titre"
                value={titre}
                onChange={(e) => setTitre(e.target.value)}
                placeholder="Ex: Sortie au parc"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Type</Label>
                <Select value={type} onValueChange={setType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TYPES_ACTIVITE.filter((t) => t !== "tous").map((t) => (
                      <SelectItem key={t} value={t}>
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="act-date">Date *</Label>
                <Input
                  id="act-date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="act-lieu">Lieu</Label>
                <Input
                  id="act-lieu"
                  value={lieu}
                  onChange={(e) => setLieu(e.target.value)}
                  placeholder="Lieu..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="act-duree">Durée (min)</Label>
                <Input
                  id="act-duree"
                  type="number"
                  min={0}
                  value={duree}
                  onChange={(e) => setDuree(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="act-desc">Description</Label>
              <Input
                id="act-desc"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Détails..."
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueCreation(false)}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={enCreation || !titre.trim()}>
                {enCreation && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Créer
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Dialogue suggestions IA (simplifié — Phase O) */}
      <Dialog open={dialogueSuggestions} onOpenChange={setDialogueSuggestions}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Suggestions d'activités IA
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              L'IA génère des suggestions avec la météo réelle et l'âge de Jules automatiquement.
            </p>

            {/* Filtre type simple */}
            <div className="space-y-2">
              <Label>Type d'activité</Label>
              <div className="flex flex-wrap gap-2">
                {[
                  { value: "mixte", label: "Tout", icone: Cloud },
                  { value: "interieur", label: "Intérieur", icone: Home },
                  { value: "exterieur", label: "Extérieur", icone: TreePine },
                ].map(({ value, label, icone: Icone }) => (
                  <Button
                    key={value}
                    variant={typePrefere === value ? "default" : "outline"}
                    size="sm"
                    onClick={() => setTypePrefere(value)}
                  >
                    <Icone className="mr-1 h-4 w-4" />
                    {label}
                  </Button>
                ))}
              </div>
            </div>

            {/* Bouton générer */}
            <Button
              onClick={genererSuggestionsIA}
              disabled={enChargementIA}
              className="w-full"
            >
              {enChargementIA ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Génération en cours...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Générer des suggestions
                </>
              )}
            </Button>

            {/* Résultats */}
            {suggestionsIA && (
              <Card className="mt-4">
                <CardContent className="pt-5">
                  <div className="mb-3 flex flex-wrap gap-2">
                    {meteoDetectee && (
                      <Badge variant="outline" className="text-xs">
                        Météo détectée: {meteoDetectee}
                      </Badge>
                    )}
                    {journeeLibreDetectee && (
                      <Badge variant="secondary" className="text-xs">
                        Journée libre détectée
                      </Badge>
                    )}
                  </div>
                  <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                    {suggestionsIA}
                  </div>

                  {suggestionsStruct.length > 0 && (
                    <div className="mt-4 space-y-2 border-t pt-3">
                      <p className="text-xs font-medium text-muted-foreground">
                        Pré-remplissage rapide
                      </p>
                      <div className="grid gap-2 sm:grid-cols-2">
                        {suggestionsStruct.slice(0, 4).map((s, idx) => (
                          <Card key={`${s.titre}-${idx}`}>
                            <CardContent className="pt-3 space-y-2">
                              <p className="text-sm font-medium line-clamp-1">{s.titre}</p>
                              <p className="text-xs text-muted-foreground line-clamp-2">{s.description}</p>
                              <Button
                                size="sm"
                                variant="outline"
                                className="w-full"
                                onClick={() => appliquerSuggestion(s)}
                              >
                                Utiliser cette suggestion
                              </Button>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function ActiviteCard({ activite: a }: { activite: Activite }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{a.titre}</CardTitle>
          <div className="flex gap-1">
            <Badge variant="outline" className="text-xs capitalize">
              {a.type}
            </Badge>
            {a.est_terminee && (
              <Badge variant="secondary" className="text-xs">
                <Check className="mr-1 h-3 w-3" />
                Fait
              </Badge>
            )}
          </div>
        </div>
        {a.description && (
          <CardDescription>{a.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="flex flex-wrap gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <CalendarHeart className="h-3 w-3" />
          {new Date(a.date).toLocaleDateString("fr-FR", {
            weekday: "short",
            day: "numeric",
            month: "short",
          })}
        </span>
        {a.lieu && (
          <span className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {a.lieu}
          </span>
        )}
        {a.duree_minutes && (
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {a.duree_minutes} min
          </span>
        )}
        {a.participants && a.participants.length > 0 && (
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {a.participants.length}
          </span>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Dialogue Suggestions IA ──────────────────────────────

const METEO_OPTIONS = [
  { value: "soleil", label: "Soleil", icone: Sun },
  { value: "pluie", label: "Pluie", icone: CloudRain },
  { value: "nuageux", label: "Nuageux", icone: Cloud },
  { value: "interieur", label: "Intérieur", icone: Home },
  { value: "exterieur", label: "Extérieur", icone: TreePine },
] as const;

const PREFERENCES_OPTIONS = [
  { value: "creatif", label: "Créatif", icone: Palette },
  { value: "sportif", label: "Sportif", icone: Dumbbell },
  { value: "educatif", label: "Éducatif", icone: BookOpen },
  { value: "sensoriel", label: "Sensoriel", icone: Puzzle },
] as const;

function DialogueSuggestionsIA({
  ouvert,
  onOpenChange,
}: {
  ouvert: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [ageMois, setAgeMois] = useState("36");
  const [meteo, setMeteo] = useState("mixte");
  const [budgetMax, setBudgetMax] = useState("50");
  const [dureeMin, setDureeMin] = useState("30");
  const [dureeMax, setDureeMax] = useState("120");
  const [preferences, setPreferences] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<SuggestionActivite[]>([]);
  const [enChargement, setEnChargement] = useState(false);

  const togglePreference = (pref: string) => {
    setPreferences((prev) =>
      prev.includes(pref) ? prev.filter((p) => p !== pref) : [...prev, pref]
    );
  };

  const genererSuggestions = async () => {
    setEnChargement(true);
    try {
      const resultat = await obtenirSuggestionsActivites({
        age_mois: Number(ageMois),
        meteo,
        budget_max: Number(budgetMax),
        duree_min: Number(dureeMin),
        duree_max: Number(dureeMax),
        preferences: preferences.length > 0 ? preferences : undefined,
        nb_suggestions: 5,
      });
      setSuggestions(resultat.suggestions);
      toast.success(`${resultat.total} suggestions générées`);
    } catch {
      toast.error("Erreur lors de la génération des suggestions");
    } finally {
      setEnChargement(false);
    }
  };

  return (
    <Dialog open={ouvert} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Suggestions d&apos;activités IA
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Paramètres */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="ia-age">Âge de l&apos;enfant (mois)</Label>
              <Input
                id="ia-age"
                type="number"
                min={0}
                max={72}
                value={ageMois}
                onChange={(e) => setAgeMois(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Budget max (€)</Label>
              <Input
                type="number"
                min={0}
                max={500}
                value={budgetMax}
                onChange={(e) => setBudgetMax(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Durée min (min)</Label>
              <Input
                type="number"
                min={5}
                max={300}
                value={dureeMin}
                onChange={(e) => setDureeMin(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Durée max (min)</Label>
              <Input
                type="number"
                min={10}
                max={360}
                value={dureeMax}
                onChange={(e) => setDureeMax(e.target.value)}
              />
            </div>
          </div>

          {/* Météo */}
          <div className="space-y-2">
            <Label>Météo / Lieu</Label>
            <div className="flex flex-wrap gap-2">
              {METEO_OPTIONS.map(({ value, label, icone: Icone }) => (
                <Button
                  key={value}
                  variant={meteo === value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMeteo(value)}
                >
                  <Icone className="mr-1 h-4 w-4" />
                  {label}
                </Button>
              ))}
            </div>
          </div>

          {/* Préférences */}
          <div className="space-y-2">
            <Label>Préférences</Label>
            <div className="flex flex-wrap gap-2">
              {PREFERENCES_OPTIONS.map(({ value, label, icone: Icone }) => (
                <Button
                  key={value}
                  variant={preferences.includes(value) ? "default" : "outline"}
                  size="sm"
                  onClick={() => togglePreference(value)}
                >
                  <Icone className="mr-1 h-4 w-4" />
                  {label}
                </Button>
              ))}
            </div>
          </div>

          {/* Bouton générer */}
          <Button
            onClick={genererSuggestions}
            disabled={enChargement}
            className="w-full"
          >
            {enChargement ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Génération en cours...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Générer des suggestions
              </>
            )}
          </Button>

          {/* Résultats */}
          {suggestions.length > 0 && (
            <div className="space-y-3 pt-2 border-t">
              <h3 className="font-semibold">
                {suggestions.length} activités suggérées
              </h3>
              <div className="grid gap-3 sm:grid-cols-2">
                {suggestions.map((s, i) => (
                  <SuggestionCard key={i} suggestion={s} />
                ))}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function SuggestionCard({ suggestion: s }: { suggestion: SuggestionActivite }) {
  const lieuIcone = s.lieu === "interieur" ? Home : s.lieu === "exterieur" ? TreePine : Cloud;
  const LieuIcone = lieuIcone;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{s.nom}</CardTitle>
        <CardDescription className="text-xs">{s.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge variant="outline" className="gap-1">
            <Timer className="h-3 w-3" />
            {s.duree_minutes} min
          </Badge>
          <Badge variant="outline" className="gap-1">
            <Euro className="h-3 w-3" />
            {s.budget === 0 ? "Gratuit" : `${s.budget}€`}
          </Badge>
          <Badge variant="outline" className="gap-1 capitalize">
            <LieuIcone className="h-3 w-3" />
            {s.lieu}
          </Badge>
          <Badge variant="outline" className="gap-1 capitalize">
            <Dumbbell className="h-3 w-3" />
            {s.niveau_effort}
          </Badge>
        </div>
        {s.competences.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {s.competences.map((c) => (
              <Badge key={c} variant="secondary" className="text-xs">
                {c}
              </Badge>
            ))}
          </div>
        )}
        {s.materiel.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Matériel: {s.materiel.join(", ")}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
