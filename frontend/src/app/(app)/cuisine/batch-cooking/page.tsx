// ═══════════════════════════════════════════════════════════
// Batch Cooking — Sessions de cuisine en lot
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import {
  Plus,
  CookingPot,
  Clock,
  Trash2,
  Loader2,
  ChevronRight,
  CheckCircle2,
  PlayCircle,
  Snowflake,
  AlertTriangle,
  CalendarPlus,
  UtensilsCrossed,
  Timer,
  Search,
  X,
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
import { SkeletonPage } from "@/composants/ui/skeleton-page";
import { EtatVide } from "@/composants/ui/etat-vide";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerSessionsBatch,
  creerSessionBatch,
  supprimerSessionBatch,
  listerPreparations,
  consommerPreparation,
} from "@/bibliotheque/api/batch-cooking";
import { listerRecettes } from "@/bibliotheque/api/recettes";
import { toast } from "sonner";
import type { SessionBatchCooking } from "@/types/batch-cooking";
import type { Recette } from "@/types/recettes";
import { TimelineBatchCooking } from "@/composants/cuisine/timeline-batch-cooking";

const BADGES_STATUT: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  planifiee: { label: "Planifié", variant: "outline" },
  en_cours: { label: "En cours", variant: "default" },
  terminee: { label: "Terminé", variant: "secondary" },
  annulee: { label: "Annulé", variant: "destructive" },
  pause: { label: "En pause", variant: "outline" },
};

type FiltreLocalisation = "tout" | "frigo" | "congelateur";

const FILTRES_LOCALISATION: { valeur: FiltreLocalisation; label: string }[] = [
  { valeur: "tout", label: "Tout" },
  { valeur: "frigo", label: "🧊 Frigo" },
  { valeur: "congelateur", label: "❄️ Congélateur" },
];

function classeProgression(progression: number) {
  const pourcentage = Math.max(0, Math.min(100, Math.round(progression / 10) * 10));
  const classes: Record<number, string> = {
    0: "w-0",
    10: "w-[10%]",
    20: "w-[20%]",
    30: "w-[30%]",
    40: "w-[40%]",
    50: "w-[50%]",
    60: "w-[60%]",
    70: "w-[70%]",
    80: "w-[80%]",
    90: "w-[90%]",
    100: "w-full",
  };
  return classes[pourcentage] ?? "w-0";
}

export default function PageBatchCooking() {
  const [dialogueCreation, setDialogueCreation] = useState(false);
  const [nomSession, setNomSession] = useState("");
  const [dateSession, setDateSession] = useState("");
  const [dureeEstimee, setDureeEstimee] = useState("");
  const [filtreLocalisation, setFiltreLocalisation] = useState<FiltreLocalisation>("tout");
  const [etapeCreation, setEtapeCreation] = useState<1 | 2>(1);
  const [recettesSelectionnees, setRecettesSelectionnees] = useState<number[]>([]);
  const [rechercheRecette, setRechercheRecette] = useState("");

  const invalider = utiliserInvalidation();

  const { data: donnees, isLoading } = utiliserRequete(
    ["batch-cooking"],
    () => listerSessionsBatch()
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    () =>
      creerSessionBatch({
        nom: nomSession.trim(),
        date_session: dateSession || undefined,
        duree_estimee: dureeEstimee ? Number(dureeEstimee) : undefined,
        recettes_selectionnees: recettesSelectionnees.length > 0 ? recettesSelectionnees : undefined,
      }),
    {
      onSuccess: () => {
        invalider(["batch-cooking"]);
        reinitialiserDialogue();
        toast.success("Session créée");
      },
      onError: () => toast.error("Erreur lors de la création"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (id: number) => supprimerSessionBatch(id),
    {
      onSuccess: () => { invalider(["batch-cooking"]); toast.success("Session supprimée"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const sessions = donnees?.items ?? [];

  const { data: toutesRecettes, isLoading: chargementRecettes } = utiliserRequete(
    ["recettes", "batch-picker"],
    () => listerRecettes(1, 100),
    { enabled: dialogueCreation && etapeCreation === 2 }
  );

  const recettesFiltrees = useMemo(() => {
    const items = toutesRecettes?.items ?? [];
    if (!rechercheRecette.trim()) return items;
    const q = rechercheRecette.toLowerCase();
    return items.filter((r) => r.nom.toLowerCase().includes(q));
  }, [toutesRecettes, rechercheRecette]);

  function toggleRecette(id: number) {
    setRecettesSelectionnees((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  function reinitialiserDialogue() {
    setDialogueCreation(false);
    setNomSession("");
    setDateSession("");
    setDureeEstimee("");
    setEtapeCreation(1);
    setRecettesSelectionnees([]);
    setRechercheRecette("");
  }

  const { data: preparationsDonnees } = utiliserRequete(
    ["batch-cooking", "preparations"],
    () => listerPreparations(false)
  );

  const preparations = preparationsDonnees?.items ?? [];

  const { mutate: consommer, isPending: enConsommation } = utiliserMutation(
    (id: number) => consommerPreparation(id),
    {
      onSuccess: (result) => {
        invalider(["batch-cooking", "preparations"]);
        if (result.consomme) {
          toast.success(`${result.nom} terminé !`);
        } else {
          toast.success(`1 portion consommée — ${result.portions_restantes} restante(s)`);
        }
      },
    }
  );

  const preparationsFiltrees =
    filtreLocalisation === "tout"
      ? preparations
      : preparations.filter((p) => p.localisation === filtreLocalisation);

  if (isLoading && !donnees) {
    return (
      <SkeletonPage
        ariaLabel="Chargement du batch cooking"
        lignes={["h-8 w-44", "h-10 w-64", "h-52 w-full"]}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            🍳 Batch Cooking
          </h1>
          <p className="text-muted-foreground">
            Planifiez et gérez vos sessions de cuisine en lot
          </p>
        </div>
        <Button onClick={() => setDialogueCreation(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Nouvelle session
        </Button>
      </div>

      {sessions.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Timeline de préparation</CardTitle>
            <CardDescription>
              Lecture animée des prochaines sessions et de leur progression.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TimelineBatchCooking sessions={sessions} />
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="sessions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="sessions">
            <CookingPot className="mr-1 h-4 w-4" />
            Sessions
          </TabsTrigger>
          <TabsTrigger value="stock">
            <Snowflake className="mr-1 h-4 w-4" />
            En stock
            {preparations.length > 0 && (
              <Badge variant="secondary" className="ml-1.5 text-xs px-1.5 py-0">
                {preparations.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="planifier">
            <CalendarPlus className="mr-1 h-4 w-4" />
            Planifier repas
          </TabsTrigger>
        </TabsList>

        {/* ═════ Onglet Sessions ═════ */}
        <TabsContent value="sessions">
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-44" />
          ))}
        </div>
      ) : sessions.length === 0 ? (
        <EtatVide
          Icone={CookingPot}
          titre="Aucune session de batch cooking"
          description="Créez une première session pour préparer plusieurs repas d’avance et gagner du temps dans la semaine."
          action={
            <Button variant="outline" onClick={() => setDialogueCreation(true)}>
              <Plus className="mr-1 h-4 w-4" />
              Créer une session
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sessions.map((s) => (
            <SessionCard
              key={s.id}
              session={s}
              onSupprimer={() => supprimer(s.id)}
            />
          ))}
        </div>
      )}
        </TabsContent>

        {/* ═════ Onglet En stock ═════ */}
        <TabsContent value="stock">
      {preparations.length > 0 ? (
        <div>
          {/* Filtres par localisation */}
          <div className="flex gap-2 mb-4">
            {FILTRES_LOCALISATION.map((f) => (
              <Button
                key={f.valeur}
                variant={filtreLocalisation === f.valeur ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltreLocalisation(f.valeur)}
              >
                {f.label}
                {f.valeur !== "tout" && (
                  <span className="ml-1 text-xs opacity-70">
                    ({preparations.filter((p) => p.localisation === f.valeur).length})
                  </span>
                )}
              </Button>
            ))}
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {preparationsFiltrees.map((p) => (
              <Card key={p.id} className={p.alerte_peremption ? "border-orange-300" : ""}>
                <CardContent className="pt-4">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <p className="font-medium text-sm truncate">{p.nom}</p>
                      {p.localisation && (
                        <p className="text-xs text-muted-foreground capitalize">{p.localisation}</p>
                      )}
                    </div>
                    {p.alerte_peremption && (
                      <AlertTriangle className="h-4 w-4 text-orange-500 shrink-0" />
                    )}
                  </div>
                  <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
                    {p.portions_restantes != null && (
                      <span>
                        🍽️ {p.portions_restantes}
                        {p.portions_initiales ? `/${p.portions_initiales}` : ""} portions
                      </span>
                    )}
                    {p.date_peremption && (
                      <span className={p.alerte_peremption ? "text-orange-600 font-medium" : ""}>
                        📅 {new Date(p.date_peremption).toLocaleDateString("fr-FR")}
                        {p.jours_avant_peremption != null && ` (${p.jours_avant_peremption}j)`}
                      </span>
                    )}
                  </div>
                  {/* Bouton consommer */}
                  {(p.portions_restantes ?? 0) > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-3 w-full"
                      disabled={enConsommation}
                      onClick={() => consommer(p.id)}
                    >
                      {enConsommation ? (
                        <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                      ) : (
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                      )}
                      Consommer 1 portion
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
            {preparationsFiltrees.length === 0 && (
              <EtatVide
                Icone={Snowflake}
                titre="Aucune préparation dans cette catégorie"
                description="Changez le filtre ou terminez une session pour remplir ce stock."
                className="col-span-full p-6"
              />
            )}
          </div>
        </div>
      ) : (
        <EtatVide
          Icone={Snowflake}
          titre="Aucune préparation en stock"
          description="Terminez une session batch cooking pour avoir des portions disponibles au frigo ou au congélateur."
        />
      )}
        </TabsContent>

        {/* ═════ Onglet Planifier repas ═════ */}
        <TabsContent value="planifier">
      {preparations.filter((p) => (p.portions_restantes ?? 0) > 0).length > 0 ? (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Sélectionnez des préparations en stock pour les intégrer à votre planning repas de la semaine.
          </p>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {preparations
              .filter((p) => (p.portions_restantes ?? 0) > 0)
              .map((p) => (
                <Card key={p.id} className="hover:bg-accent/30 transition-colors">
                  <CardContent className="pt-4">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-medium text-sm truncate">{p.nom}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          🍽️ {p.portions_restantes} portion{(p.portions_restantes ?? 0) > 1 ? "s" : ""} disponible{(p.portions_restantes ?? 0) > 1 ? "s" : ""}
                        </p>
                      </div>
                      {p.localisation && (
                        <Badge variant="outline" className="text-xs capitalize shrink-0">
                          {p.localisation}
                        </Badge>
                      )}
                    </div>
                    {p.date_peremption && (
                      <p className={`text-xs mt-2 ${p.alerte_peremption ? "text-orange-600 font-medium" : "text-muted-foreground"}`}>
                        {p.alerte_peremption && <AlertTriangle className="inline h-3 w-3 mr-1" />}
                        À consommer avant le {new Date(p.date_peremption).toLocaleDateString("fr-FR")}
                        {p.jours_avant_peremption != null && ` (${p.jours_avant_peremption}j)`}
                      </p>
                    )}
                    <Link href={`/cuisine/planning?preparation=${p.id}`}>
                      <Button variant="outline" size="sm" className="mt-3 w-full">
                        <UtensilsCrossed className="mr-1 h-3 w-3" />
                        Ajouter au planning
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
          </div>
        </div>
      ) : (
        <EtatVide
          Icone={CalendarPlus}
          titre="Aucune préparation disponible"
          description="Il faut des portions restantes pour injecter un plat batch cooking dans le planning de la semaine."
        />
      )}
        </TabsContent>
      </Tabs>

      {/* Dialogue création */}
      <Dialog open={dialogueCreation} onOpenChange={(open) => { if (!open) reinitialiserDialogue(); else setDialogueCreation(true); }}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              Nouvelle session
              <span className="ml-2 text-sm font-normal text-muted-foreground">
                Étape {etapeCreation}/2
              </span>
            </DialogTitle>
          </DialogHeader>

          {etapeCreation === 1 ? (
            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                if (nomSession.trim()) setEtapeCreation(2);
              }}
            >
              <div className="space-y-2">
                <Label htmlFor="bc-nom">Nom de la session *</Label>
                <Input
                  id="bc-nom"
                  value={nomSession}
                  onChange={(e) => setNomSession(e.target.value)}
                  placeholder="Ex: Batch du dimanche"
                  autoFocus
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bc-date">Date</Label>
                  <Input
                    id="bc-date"
                    type="date"
                    value={dateSession}
                    onChange={(e) => setDateSession(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bc-duree">Durée estimée (min)</Label>
                  <Input
                    id="bc-duree"
                    type="number"
                    min={0}
                    value={dureeEstimee}
                    onChange={(e) => setDureeEstimee(e.target.value)}
                    placeholder="120"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="outline" onClick={reinitialiserDialogue}>
                  Annuler
                </Button>
                <Button type="submit" disabled={!nomSession.trim()}>
                  Suivant : choisir les recettes
                  <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Sélectionnez les recettes à préparer lors de cette session.
                {recettesSelectionnees.length > 0 && (
                  <span className="ml-1 font-medium text-foreground">
                    {recettesSelectionnees.length} sélectionnée{recettesSelectionnees.length > 1 ? "s" : ""}
                  </span>
                )}
              </p>

              {/* Recherche */}
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  className="pl-8"
                  placeholder="Rechercher une recette…"
                  value={rechercheRecette}
                  onChange={(e) => setRechercheRecette(e.target.value)}
                  autoFocus
                />
                {rechercheRecette && (
                  <button
                    type="button"
                    aria-label="Effacer la recherche"
                    className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-foreground"
                    onClick={() => setRechercheRecette("")}
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>

              {/* Liste recettes */}
              <div className="max-h-64 overflow-y-auto space-y-1 rounded-md border p-2">
                {chargementRecettes ? (
                  <div className="flex justify-center py-6">
                    <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                  </div>
                ) : recettesFiltrees.length === 0 ? (
                  <p className="py-4 text-center text-sm text-muted-foreground">Aucune recette trouvée</p>
                ) : (
                  recettesFiltrees.map((r) => {
                    const selectionne = recettesSelectionnees.includes(r.id);
                    return (
                      <button
                        key={r.id}
                        type="button"
                        className={`w-full flex items-center justify-between gap-2 rounded px-3 py-2 text-left text-sm transition-colors hover:bg-accent ${
                          selectionne ? "bg-primary/10 font-medium" : ""
                        }`}
                        onClick={() => toggleRecette(r.id)}
                      >
                        <span className="min-w-0 truncate">{r.nom}</span>
                        <div className="flex items-center gap-2 shrink-0">
                          {r.temps_preparation != null && (
                            <span className="text-xs text-muted-foreground">{r.temps_preparation + (r.temps_cuisson ?? 0)} min</span>
                          )}
                          {selectionne && <CheckCircle2 className="h-4 w-4 text-primary" />}
                        </div>
                      </button>
                    );
                  })
                )}
              </div>

              <div className="flex justify-between gap-2">
                <Button type="button" variant="outline" onClick={() => setEtapeCreation(1)}>
                  Retour
                </Button>
                <div className="flex gap-2">
                  <Button type="button" variant="ghost" onClick={reinitialiserDialogue}>
                    Annuler
                  </Button>
                  <Button
                    type="button"
                    disabled={enCreation}
                    onClick={() => creer(undefined)}
                  >
                    {enCreation && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Créer la session
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function SessionCard({
  session,
  onSupprimer,
}: {
  session: SessionBatchCooking;
  onSupprimer: () => void;
}) {
  const badge = BADGES_STATUT[session.statut] ?? BADGES_STATUT.planifiee;
  const IconeStatut =
    session.statut === "terminee"
      ? CheckCircle2
      : session.statut === "en_cours"
        ? PlayCircle
        : Clock;

  return (
    <Card className="hover:bg-accent/30 transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-base">{session.nom}</CardTitle>
            {session.date_session && (
              <CardDescription>
                {new Date(session.date_session).toLocaleDateString("fr-FR", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                })}
              </CardDescription>
            )}
          </div>
          <Badge variant={badge.variant} className="text-xs shrink-0">
            {badge.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <IconeStatut className="h-3.5 w-3.5" />
            {session.etapes_count} étape{session.etapes_count > 1 ? "s" : ""}
          </span>
          {session.duree_estimee && (
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {session.duree_estimee} min
              <Link href={`/outils/minuteur?minutes=${session.duree_estimee}`}>
                <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                  <Timer className="h-3 w-3 mr-1" />
                  Minuteur
                </Button>
              </Link>
            </span>
          )}
          {session.recettes_selectionnees.length > 0 && (
            <span>
              {session.recettes_selectionnees.length} recette
              {session.recettes_selectionnees.length > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Progress bar */}
        {session.statut === "en_cours" && (
          <div className="w-full bg-secondary rounded-full h-2">
            <div
              className={`bg-primary rounded-full h-2 transition-all ${classeProgression(Math.round(session.progression * 100))}`}
            />
          </div>
        )}

        <div className="flex justify-between">
          <Button variant="ghost" size="sm" onClick={onSupprimer}>
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
          <Link href={`/cuisine/batch-cooking/${session.id}`}>
            <Button variant="ghost" size="sm">
              Détails
              <ChevronRight className="ml-1 h-3.5 w-3.5" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
