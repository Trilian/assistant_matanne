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
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerSessionsBatch,
  creerSessionBatch,
  supprimerSessionBatch,
} from "@/bibliotheque/api/batch-cooking";
import { toast } from "sonner";
import type { SessionBatchCooking } from "@/types/batch-cooking";

const BADGES_STATUT: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  planifie: { label: "Planifié", variant: "outline" },
  en_cours: { label: "En cours", variant: "default" },
  termine: { label: "Terminé", variant: "secondary" },
  annule: { label: "Annulé", variant: "destructive" },
};

export default function PageBatchCooking() {
  const [dialogueCreation, setDialogueCreation] = useState(false);
  const [nomSession, setNomSession] = useState("");
  const [dateSession, setDateSession] = useState("");
  const [dureeEstimee, setDureeEstimee] = useState("");

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
