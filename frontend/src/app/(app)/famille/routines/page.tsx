// ═══════════════════════════════════════════════════════════
// Routines familiales — Matin / Soir / Journée
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Plus,
  ListChecks,
  Sun,
  Moon,
  CalendarDays,
  Trash2,
  Loader2,
  Check,
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/hooks/utiliser-api";
import {
  listerRoutines,
  creerRoutine,
  supprimerRoutine,
} from "@/lib/api/famille";
import type { Routine, EtapeRoutine } from "@/types/famille";

const TYPES_ROUTINE = [
  { valeur: "matin", label: "Matin", Icone: Sun },
  { valeur: "soir", label: "Soir", Icone: Moon },
  { valeur: "journee", label: "Journée", Icone: CalendarDays },
] as const;

export default function PageRoutines() {
  const [dialogueCreation, setDialogueCreation] = useState(false);
  const [nom, setNom] = useState("");
  const [type, setType] = useState<"matin" | "soir" | "journee">("matin");
  const [etapes, setEtapes] = useState<{ titre: string; duree_minutes?: number }[]>([
    { titre: "" },
  ]);

  const invalider = utiliserInvalidation();

  const { data: routines, isLoading } = utiliserRequete(
    ["famille", "routines"],
    listerRoutines
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (routine: Omit<Routine, "id">) => creerRoutine(routine),
    {
      onSuccess: () => {
        invalider(["famille", "routines"]);
        setDialogueCreation(false);
        setNom("");
        setEtapes([{ titre: "" }]);
      },
    }
  );

  const { mutate: supprimer } = utiliserMutation(
    (id: number) => supprimerRoutine(id),
    { onSuccess: () => invalider(["famille", "routines"]) }
  );

  const ajouterEtape = () => setEtapes([...etapes, { titre: "" }]);
  const retirerEtape = (idx: number) =>
    setEtapes(etapes.filter((_, i) => i !== idx));
  const majEtape = (idx: number, field: string, value: string | number) =>
    setEtapes(etapes.map((e, i) => (i === idx ? { ...e, [field]: value } : e)));

  const routinesMatin = (routines ?? []).filter((r) => r.type === "matin");
  const routinesSoir = (routines ?? []).filter((r) => r.type === "soir");
  const routinesJournee = (routines ?? []).filter((r) => r.type === "journee");

  const groupes = [
    { type: "matin" as const, label: "Matin", Icone: Sun, items: routinesMatin },
    { type: "soir" as const, label: "Soir", Icone: Moon, items: routinesSoir },
    { type: "journee" as const, label: "Journée", Icone: CalendarDays, items: routinesJournee },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📋 Routines</h1>
          <p className="text-muted-foreground">
            Routines quotidiennes familiales
          </p>
        </div>
        <Button onClick={() => setDialogueCreation(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Nouvelle routine
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      ) : !routines?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <ListChecks className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucune routine définie</p>
            <Button
              variant="outline"
              onClick={() => setDialogueCreation(true)}
            >
              <Plus className="mr-1 h-4 w-4" />
              Créer une routine
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {groupes.map(({ type: t, label, Icone, items }) => (
            <div key={t} className="space-y-3">
              <div className="flex items-center gap-2">
                <Icone className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">{label}</h2>
                <Badge variant="secondary" className="text-xs">
                  {items.length}
                </Badge>
              </div>
              {items.length === 0 ? (
                <Card>
                  <CardContent className="py-6 text-center text-sm text-muted-foreground">
                    Aucune routine {label.toLowerCase()}
                  </CardContent>
                </Card>
              ) : (
                items.map((r) => (
                  <RoutineCard
                    key={r.id}
                    routine={r}
                    onSupprimer={() => supprimer(r.id)}
                  />
                ))
              )}
            </div>
          ))}
        </div>
      )}

      {/* Dialogue création */}
      <Dialog open={dialogueCreation} onOpenChange={setDialogueCreation}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Nouvelle routine</DialogTitle>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (!nom.trim() || etapes.every((s) => !s.titre.trim())) return;
              creer({
                nom: nom.trim(),
                type,
                est_active: true,
                etapes: etapes
                  .filter((s) => s.titre.trim())
                  .map((s, i) => ({
                    id: 0,
                    titre: s.titre.trim(),
                    duree_minutes: s.duree_minutes,
                    ordre: i + 1,
                    est_terminee: false,
                  })),
              });
            }}
          >
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="routine-nom">Nom *</Label>
                <Input
                  id="routine-nom"
                  value={nom}
                  onChange={(e) => setNom(e.target.value)}
                  placeholder="Ex: Routine du matin"
                />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select
                  value={type}
                  onValueChange={(v) => setType(v as typeof type)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TYPES_ROUTINE.map((t) => (
                      <SelectItem key={t.valeur} value={t.valeur}>
                        {t.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Étapes</Label>
              <div className="space-y-2">
                {etapes.map((s, i) => (
                  <div key={i} className="flex gap-2">
                    <Input
                      placeholder={`Étape ${i + 1}`}
                      value={s.titre}
                      onChange={(e) => majEtape(i, "titre", e.target.value)}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      min={0}
                      placeholder="min"
                      className="w-20"
                      value={s.duree_minutes ?? ""}
                      onChange={(e) =>
                        majEtape(
                          i,
                          "duree_minutes",
                          e.target.value ? Number(e.target.value) : 0
                        )
                      }
                    />
                    {etapes.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => retirerEtape(i)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              <Button type="button" variant="outline" size="sm" onClick={ajouterEtape}>
                <Plus className="mr-1 h-3 w-3" />
                Étape
              </Button>
            </div>

            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueCreation(false)}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={enCreation || !nom.trim()}>
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

function RoutineCard({
  routine,
  onSupprimer,
}: {
  routine: Routine;
  onSupprimer: () => void;
}) {
  const etapesTerminees = routine.etapes.filter((e) => e.est_terminee).length;
  const total = routine.etapes.length;

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base">{routine.nom}</CardTitle>
            <CardDescription className="text-xs">
              {etapesTerminees}/{total} étapes complétées
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 shrink-0"
            onClick={onSupprimer}
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {routine.etapes
            .sort((a, b) => a.ordre - b.ordre)
            .map((e) => (
              <div
                key={e.id}
                className={`flex items-center gap-2 text-sm rounded px-2 py-1 ${
                  e.est_terminee ? "opacity-50 line-through" : ""
                }`}
              >
                <div
                  className={`h-4 w-4 rounded-full border flex items-center justify-center shrink-0 ${
                    e.est_terminee
                      ? "bg-primary border-primary"
                      : "border-muted-foreground"
                  }`}
                >
                  {e.est_terminee && (
                    <Check className="h-2.5 w-2.5 text-primary-foreground" />
                  )}
                </div>
                <span className="flex-1">{e.titre}</span>
                {e.duree_minutes != null && e.duree_minutes > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {e.duree_minutes}m
                  </span>
                )}
              </div>
            ))}
        </div>
      </CardContent>
    </Card>
  );
}
