// ═══════════════════════════════════════════════════════════
// Suivi Jules — Développement enfant
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Baby,
  Plus,
  Star,
  Calendar,
  Loader2,
  Footprints,
  MessageCircle,
  Brain,
  Heart,
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
  obtenirProfilJules,
  listerJalons,
  ajouterJalon,
  obtenirAlimentsExclus,
  obtenirCoachingHebdo,
  sauvegarderAlimentsExclus,
  listerActivites,
  listerRoutines,
  obtenirSuggestionsActivitesAuto,
  obtenirSuggestionsAchatsAuto,
  creerActivite,
} from "@/bibliotheque/api/famille";
import { obtenirTableauBord } from "@/bibliotheque/api/tableau-bord";
import dynamic from "next/dynamic";
import type { JalonJules } from "@/types/famille";
import { toast } from "sonner";

const GraphiqueJalons = dynamic(
  () => import("@/composants/graphiques/graphique-jalons").then((m) => m.GraphiqueJalons),
  { ssr: false }
);

const CATEGORIES_JALONS = [
  { valeur: "motricite", label: "Motricité", Icone: Footprints },
  { valeur: "langage", label: "Langage", Icone: MessageCircle },
  { valeur: "cognitif", label: "Cognitif", Icone: Brain },
  { valeur: "social", label: "Social", Icone: Heart },
  { valeur: "autre", label: "Autre", Icone: Star },
];

function iconeCategorie(cat: string) {
  const found = CATEGORIES_JALONS.find((c) => c.valeur === cat);
  return found ? found.Icone : Star;
}

export default function PageJules() {
  const [categorieFiltre, setCategorieFiltre] = useState("tous");
  const [dialogueAjout, setDialogueAjout] = useState(false);
  const [nouvelAliment, setNouvelAliment] = useState("");

  // Form state
  const [titre, setTitre] = useState("");
  const [categorie, setCategorie] = useState("motricite");
  const [description, setDescription] = useState("");
  const [dateObs, setDateObs] = useState("");

  const invalider = utiliserInvalidation();
  const aujourdHuiIso = new Date().toISOString().slice(0, 10);

  const { data: profil } = utiliserRequete(
    ["famille", "jules", "profil"],
    obtenirProfilJules
  );

  const { data: jalons, isLoading } = utiliserRequete(
    ["famille", "jules", "jalons", categorieFiltre],
    () =>
      listerJalons(categorieFiltre !== "tous" ? categorieFiltre : undefined)
  );

  const { data: alimentsExclus } = utiliserRequete(
    ["famille", "jules", "aliments-exclus"],
    obtenirAlimentsExclus
  );

  const { data: coaching } = utiliserRequete(
    ["famille", "jules", "coaching-hebdo"],
    obtenirCoachingHebdo
  );

  const { data: activitesJour } = utiliserRequete(
    ["famille", "jules", "activites-jour", aujourdHuiIso],
    () => listerActivites(undefined, aujourdHuiIso)
  );

  const { data: routines } = utiliserRequete(
    ["famille", "jules", "routines"],
    listerRoutines
  );

  const { data: suggestionsActivites } = utiliserRequete(
    ["famille", "jules", "suggestions-activites-auto"],
    () => obtenirSuggestionsActivitesAuto({ budget_max: 40, duree_max_heures: 2 })
  );

  const { data: suggestionsAchats } = utiliserRequete(
    ["famille", "jules", "suggestions-achats-auto"],
    () => obtenirSuggestionsAchatsAuto({ budget_max: 80 })
  );

  const { data: dashboardJour } = utiliserRequete(
    ["famille", "jules", "repas-jour"],
    obtenirTableauBord
  );

  const { mutate: ajouter, isPending: enAjout } = utiliserMutation(
    (jalon: Omit<JalonJules, "id">) => ajouterJalon(jalon),
    {
      onSuccess: () => {
        invalider(["famille", "jules", "jalons"]);
        setDialogueAjout(false);
        setTitre("");
        setDescription("");
        setDateObs("");
        toast.success("Jalon ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: enregistrerAliments, isPending: enSauvegardeAliments } = utiliserMutation(
    (items: string[]) => sauvegarderAlimentsExclus(items),
    {
      onSuccess: () => {
        invalider(["famille", "jules", "aliments-exclus"]);
        setNouvelAliment("");
        toast.success("Aliments exclus mis à jour");
      },
      onError: () => toast.error("Impossible d'enregistrer les aliments exclus"),
    }
  );

  const { mutate: validerSuggestionActivite, isPending: enValidationSuggestion } = utiliserMutation(
    async (suggestion: { titre: string; description?: string; type?: string; duree_minutes?: number; lieu?: string }) => {
      return creerActivite({
        titre: suggestion.titre,
        description: suggestion.description,
        type: suggestion.type || "jules",
        date: aujourdHuiIso,
        duree_minutes: suggestion.duree_minutes,
        lieu: suggestion.lieu,
        participants: ["Jules"],
        est_terminee: false,
      });
    },
    {
      onSuccess: () => {
        invalider(["famille", "jules", "activites-jour"]);
        toast.success("Suggestion ajoutée aux activités du jour");
      },
      onError: () => toast.error("Impossible d'ajouter la suggestion"),
    }
  );

  // Calcul âge en mois
  const ageMois = profil?.date_naissance
    ? Math.floor(
        (Date.now() - new Date(profil.date_naissance).getTime()) /
          (1000 * 60 * 60 * 24 * 30.44)
      )
    : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">👶 Jules</h1>
          <p className="text-muted-foreground">
            Suivi du développement
            {ageMois !== null && ` — ${ageMois} mois`}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/famille/activites?pour_qui=jules">
            <Button variant="outline" size="sm">
              <Calendar className="mr-1 h-4 w-4" />
              Activités Jules
            </Button>
          </Link>
          <Button onClick={() => setDialogueAjout(true)}>
            <Plus className="mr-1 h-4 w-4" />
            Nouveau jalon
          </Button>
        </div>
      </div>

      {/* Résumé catégories */}
      <div className="grid gap-3 grid-cols-2 sm:grid-cols-5">
        {CATEGORIES_JALONS.map(({ valeur, label, Icone }) => {
          return (
            <Card
              key={valeur}
              className={`cursor-pointer transition-colors hover:bg-accent/50 ${
                categorieFiltre === valeur ? "border-primary" : ""
              }`}
              onClick={() =>
                setCategorieFiltre(categorieFiltre === valeur ? "tous" : valeur)
              }
            >
              <CardContent className="flex items-center gap-2 py-3 px-4">
                <Icone className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">{label}</span>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Hub Jules unifié */}
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Timeline du jour</CardTitle>
            <CardDescription>Routines, activités et repas du jour</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {(routines ?? []).slice(0, 3).map((routine) => (
              <div key={`routine-${routine.id}`} className="rounded-md border px-3 py-2 text-sm">
                <p className="font-medium">Routine • {routine.nom}</p>
                <p className="text-xs text-muted-foreground">{routine.type}</p>
              </div>
            ))}
            {(activitesJour ?? []).slice(0, 3).map((activite) => (
              <div key={`activite-${activite.id}`} className="rounded-md border px-3 py-2 text-sm">
                <p className="font-medium">Activité • {activite.titre}</p>
                <p className="text-xs text-muted-foreground">{activite.type}</p>
              </div>
            ))}
            {(dashboardJour?.repas_aujourd_hui ?? []).slice(0, 2).map((repas, idx) => (
              <div key={`repas-${idx}`} className="rounded-md border px-3 py-2 text-sm">
                <p className="font-medium">Repas • {repas.type_repas}</p>
                <p className="text-xs text-muted-foreground">{repas.recette_nom ?? "À définir"}</p>
              </div>
            ))}
            {(routines?.length ?? 0) + (activitesJour?.length ?? 0) + (dashboardJour?.repas_aujourd_hui?.length ?? 0) === 0 && (
              <p className="text-sm text-muted-foreground">Aucun élément pour la journée.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Suggestion IA</CardTitle>
            <CardDescription>1 clic pour valider</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {suggestionsActivites?.suggestions_struct?.[0] ? (
              <>
                <div className="rounded-md border px-3 py-2">
                  <p className="text-sm font-medium">{suggestionsActivites.suggestions_struct[0].titre}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {suggestionsActivites.suggestions_struct[0].description}
                  </p>
                </div>
                <Button
                  size="sm"
                  className="w-full"
                  disabled={enValidationSuggestion}
                  onClick={() => validerSuggestionActivite(suggestionsActivites.suggestions_struct![0])}
                >
                  {enValidationSuggestion && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Valider l'activité
                </Button>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Pas de suggestion disponible.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Achats recommandés</CardTitle>
          <CardDescription>Taille vêtements, éveil, saison</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {(suggestionsAchats?.suggestions ?? []).slice(0, 6).map((achat) => (
            <div key={`${achat.source}-${achat.titre}`} className="rounded-md border px-3 py-2 text-sm">
              <p className="font-medium">{achat.titre}</p>
              <p className="text-xs text-muted-foreground mt-1">{achat.description}</p>
              {achat.fourchette_prix && (
                <p className="text-xs text-muted-foreground mt-1">Budget: {achat.fourchette_prix}</p>
              )}
            </div>
          ))}
          {!(suggestionsAchats?.suggestions?.length) && (
            <p className="text-sm text-muted-foreground">Aucune recommandation d'achat pour le moment.</p>
          )}
        </CardContent>
      </Card>

      {/* Graphique jalons par catégorie */}
      {jalons && jalons.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Jalons par catégorie</CardTitle>
          </CardHeader>
          <CardContent>
            <GraphiqueJalons
              donnees={CATEGORIES_JALONS.map(({ valeur, label }) => ({
                categorie: valeur,
                label,
                nombre: jalons.filter((j) => j.categorie === valeur).length,
              })).filter((d) => d.nombre > 0)}
            />
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Aliments exclus</CardTitle>
            <CardDescription>
              Liste utilisée pour la génération des versions Jules des recettes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {(alimentsExclus?.aliments_exclus ?? []).map((aliment) => (
                <Badge key={aliment} variant="secondary">
                  {aliment}
                </Badge>
              ))}
              {!(alimentsExclus?.aliments_exclus?.length) && (
                <p className="text-sm text-muted-foreground">Aucun aliment exclu enregistré.</p>
              )}
            </div>
            <div className="flex gap-2">
              <Input
                value={nouvelAliment}
                onChange={(e) => setNouvelAliment(e.target.value)}
                placeholder="Ex: miel, fruits à coque..."
              />
              <Button
                type="button"
                variant="outline"
                disabled={enSauvegardeAliments || !nouvelAliment.trim()}
                onClick={() => {
                  const base = alimentsExclus?.aliments_exclus ?? [];
                  const prochain = Array.from(new Set([...base, nouvelAliment.trim()]));
                  enregistrerAliments(prochain);
                }}
              >
                Ajouter
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Coaching hebdo Jules</CardTitle>
            <CardDescription>{coaching?.semaine ?? "Semaine en cours"}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm">{coaching?.resume ?? "Pas encore de coaching disponible."}</p>
            {!!coaching?.conseils?.length && (
              <div>
                <p className="text-xs font-medium uppercase text-muted-foreground mb-1">Conseils</p>
                <ul className="space-y-1 text-sm list-disc pl-4">
                  {coaching.conseils.slice(0, 3).map((conseil) => (
                    <li key={conseil}>{conseil}</li>
                  ))}
                </ul>
              </div>
            )}
            {!!coaching?.alertes?.length && (
              <div>
                <p className="text-xs font-medium uppercase text-muted-foreground mb-1">Alertes</p>
                <div className="flex flex-wrap gap-2">
                  {coaching.alertes.map((alerte) => (
                    <Badge key={alerte} variant="outline">{alerte}</Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Timeline jalons */}
      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : !jalons?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <Baby className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucun jalon enregistré</p>
            <Button
              variant="outline"
              onClick={() => setDialogueAjout(true)}
            >
              <Plus className="mr-1 h-4 w-4" />
              Ajouter le premier jalon
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="relative pl-6 border-l-2 border-muted space-y-4">
          {jalons.map((j) => {
            const Icone = iconeCategorie(j.categorie);
            return (
              <div key={j.id} className="relative">
                <div className="absolute -left-[1.625rem] top-1 h-5 w-5 rounded-full bg-primary flex items-center justify-center">
                  <Icone className="h-3 w-3 text-primary-foreground" />
                </div>
                <Card>
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base">{j.titre}</CardTitle>
                        {j.description && (
                          <CardDescription className="mt-1">
                            {j.description}
                          </CardDescription>
                        )}
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {j.age_mois != null && (
                          <Badge variant="secondary" className="text-xs">
                            {j.age_mois} mois
                          </Badge>
                        )}
                        <Badge variant="outline" className="text-xs capitalize">
                          {j.categorie}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  {(j.date_observation || j.notes) && (
                    <CardContent className="pt-0 text-sm text-muted-foreground">
                      {j.date_observation && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(j.date_observation).toLocaleDateString(
                            "fr-FR"
                          )}
                        </span>
                      )}
                      {j.notes && <p className="mt-1">{j.notes}</p>}
                    </CardContent>
                  )}
                </Card>
              </div>
            );
          })}
        </div>
      )}



      {/* Dialogue ajout jalon */}
      <Dialog open={dialogueAjout} onOpenChange={setDialogueAjout}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nouveau jalon</DialogTitle>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (!titre.trim()) return;
              ajouter({
                titre: titre.trim(),
                categorie,
                description: description || undefined,
                date_observation: dateObs || undefined,
                age_mois: ageMois ?? undefined,
              });
            }}
          >
            <div className="space-y-2">
              <Label htmlFor="jalon-titre">Titre *</Label>
              <Input
                id="jalon-titre"
                value={titre}
                onChange={(e) => setTitre(e.target.value)}
                placeholder="Ex: Premiers pas"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Catégorie</Label>
                <Select value={categorie} onValueChange={setCategorie}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES_JALONS.map((c) => (
                      <SelectItem key={c.valeur} value={c.valeur}>
                        {c.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="jalon-date">Date</Label>
                <Input
                  id="jalon-date"
                  type="date"
                  value={dateObs}
                  onChange={(e) => setDateObs(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="jalon-desc">Description</Label>
              <Input
                id="jalon-desc"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Détails optionnels..."
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueAjout(false)}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={enAjout || !titre.trim()}>
                {enAjout && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Ajouter
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
