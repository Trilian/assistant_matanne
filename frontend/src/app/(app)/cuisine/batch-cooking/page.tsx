// ═══════════════════════════════════════════════════════════
// Batch Cooking — Sessions de cuisine en lot
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
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
import { toast } from "sonner";
import type { SessionBatchCooking } from "@/types/batch-cooking";

const BADGES_STATUT: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  planifie: { label: "Planifié", variant: "outline" },
  en_cours: { label: "En cours", variant: "default" },
  termine: { label: "Terminé", variant: "secondary" },
  annule: { label: "Annulé", variant: "destructive" },
};

type FiltreLocalisation = "tout" | "frigo" | "congelateur";

const FILTRES_LOCALISATION: { valeur: FiltreLocalisation; label: string }[] = [
  { valeur: "tout", label: "Tout" },
  { valeur: "frigo", label: "🧊 Frigo" },
  { valeur: "congelateur", label: "❄️ Congélateur" },
];

export default function PageBatchCooking() {
  const [dialogueCreation, setDialogueCreation] = useState(false);
  const [nomSession, setNomSession] = useState("");
  const [dateSession, setDateSession] = useState("");
  const [dureeEstimee, setDureeEstimee] = useState("");
  const [filtreLocalisation, setFiltreLocalisation] = useState<FiltreLocalisation>("tout");

  const invalider = utiliserInvalidation();

  const { data: donnees, isLoading } = utiliserRequete(
    ["batch-cooking"],
    () => listerSessionsBatch()
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (_: void) =>
      creerSessionBatch({
        nom: nomSession.trim(),
        date_session: dateSession || undefined,
        duree_estimee: dureeEstimee ? Number(dureeEstimee) : undefined,
      }),
    {
      onSuccess: () => {
        invalider(["batch-cooking"]);
        setDialogueCreation(false);
        setNomSession("");
        setDateSession("");
        setDureeEstimee("");
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
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <CookingPot className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">
              Aucune session de batch cooking
            </p>
            <Button
              variant="outline"
              onClick={() => setDialogueCreation(true)}
            >
              <Plus className="mr-1 h-4 w-4" />
              Créer une session
            </Button>
          </CardContent>
        </Card>
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
              <p className="text-sm text-muted-foreground col-span-full py-4 text-center">
                Aucune préparation dans cette catégorie.
              </p>
            )}
          </div>
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <Snowflake className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucune préparation en stock</p>
            <p className="text-xs text-muted-foreground">
              Terminez une session batch cooking pour avoir des préparations disponibles.
            </p>
          </CardContent>
        </Card>
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
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <CalendarPlus className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucune préparation disponible</p>
            <p className="text-xs text-muted-foreground">
              Il faut des préparations avec des portions restantes pour planifier des repas.
            </p>
          </CardContent>
        </Card>
      )}
        </TabsContent>
      </Tabs>

      {/* Dialogue création */}
      <Dialog open={dialogueCreation} onOpenChange={setDialogueCreation}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nouvelle session</DialogTitle>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (nomSession.trim()) creer(undefined);
            }}
          >
            <div className="space-y-2">
              <Label htmlFor="bc-nom">Nom de la session *</Label>
              <Input
                id="bc-nom"
                value={nomSession}
                onChange={(e) => setNomSession(e.target.value)}
                placeholder="Ex: Batch du dimanche"
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
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueCreation(false)}
              >
                Annuler
              </Button>
              <Button
                type="submit"
                disabled={enCreation || !nomSession.trim()}
              >
                {enCreation && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Créer
              </Button>
            </div>
          </form>
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
  const badge = BADGES_STATUT[session.statut] ?? BADGES_STATUT.planifie;
  const IconeStatut =
    session.statut === "termine"
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
              className="bg-primary rounded-full h-2 transition-all"
              style={{ width: `${Math.round(session.progression * 100)}%` }}
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
