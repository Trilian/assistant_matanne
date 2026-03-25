// ═══════════════════════════════════════════════════════════
// Planning Repas — Grille hebdomadaire
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Plus,
  X,
  Loader2,
  CalendarDays,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import { Badge } from "@/composants/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
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
  obtenirPlanningSemaine,
  definirRepas,
  supprimerRepas,
} from "@/bibliotheque/api/planning";
import { toast } from "sonner";
import type { TypeRepas, RepasPlanning } from "@/types/planning";

const JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];
const TYPES_REPAS: { valeur: TypeRepas; label: string; emoji: string }[] = [
  { valeur: "petit_dejeuner", label: "Petit-déj", emoji: "🌅" },
  { valeur: "dejeuner", label: "Déjeuner", emoji: "☀️" },
  { valeur: "gouter", label: "Goûter", emoji: "🍪" },
  { valeur: "diner", label: "Dîner", emoji: "🌙" },
];

function getLundiDeSemaine(offset: number): string {
  const now = new Date();
  const jour = now.getDay();
  const diff = jour === 0 ? -6 : 1 - jour;
  const lundi = new Date(now);
  lundi.setDate(now.getDate() + diff + offset * 7);
  return lundi.toISOString().split("T")[0];
}

function getDatesDeSemaine(dateDebut: string): string[] {
  const dates: string[] = [];
  const lundi = new Date(dateDebut);
  for (let i = 0; i < 7; i++) {
    const d = new Date(lundi);
    d.setDate(lundi.getDate() + i);
    dates.push(d.toISOString().split("T")[0]);
  }
  return dates;
}

export default function PagePlanning() {
  const [offsetSemaine, setOffsetSemaine] = useState(0);
  const [dialogueOuvert, setDialogueOuvert] = useState(false);
  const [repasEnCours, setRepasEnCours] = useState<{
    date: string;
    type_repas: TypeRepas;
  } | null>(null);
  const [notesRepas, setNotesRepas] = useState("");

  const invalider = utiliserInvalidation();
  const dateDebut = getLundiDeSemaine(offsetSemaine);
  const datesSemaine = getDatesDeSemaine(dateDebut);

  const { data: planning, isLoading } = utiliserRequete(
    ["planning", dateDebut],
    () => obtenirPlanningSemaine(dateDebut)
  );

  const { mutate: ajouterRepas, isPending: enAjout } = utiliserMutation(
    definirRepas,
    {
      onSuccess: () => {
        invalider(["planning"]);
        setDialogueOuvert(false);
        setNotesRepas("");
        toast.success("Repas ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: retirerRepas } = utiliserMutation(supprimerRepas, {
    onSuccess: () => { invalider(["planning"]); toast.success("Repas retiré"); },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  function trouverRepas(date: string, type: TypeRepas): RepasPlanning | undefined {
    return planning?.repas.find(
      (r) => r.date === date && r.type_repas === type
    );
  }

  function ouvrirDialogue(date: string, type: TypeRepas) {
    setRepasEnCours({ date, type_repas: type });
    setNotesRepas("");
    setDialogueOuvert(true);
  }

  const moisLabel = new Date(dateDebut).toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📅 Planning repas</h1>
          <p className="text-muted-foreground capitalize">{moisLabel}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setOffsetSemaine((o) => o - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setOffsetSemaine(0)}
          >
            Aujourd'hui
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setOffsetSemaine((o) => o + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Grille Planning */}
      {isLoading ? (
        <div className="grid gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {datesSemaine.map((date, idx) => {
            const dateObj = new Date(date);
            const estAujourdhui =
              date === new Date().toISOString().split("T")[0];

            return (
              <Card
                key={date}
                className={estAujourdhui ? "border-primary" : ""}
              >
                <CardHeader className="py-2 px-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">
                      {JOURS[idx]}{" "}
                      <span className="text-muted-foreground font-normal">
                        {dateObj.toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                    </CardTitle>
                    {estAujourdhui && (
                      <Badge variant="default" className="text-xs">
                        Aujourd'hui
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="py-2 px-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {TYPES_REPAS.map(({ valeur, label, emoji }) => {
                      const repas = trouverRepas(date, valeur);

                      return (
                        <div
                          key={valeur}
                          className="min-h-[48px] rounded-md border border-dashed border-muted-foreground/25 p-2 text-xs"
                        >
                          <div className="text-muted-foreground mb-1">
                            {emoji} {label}
                          </div>
                          {repas ? (
                            <div className="flex items-center justify-between gap-1">
                              <span className="font-medium text-foreground truncate">
                                {repas.recette_nom || repas.notes || "—"}
                              </span>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-5 w-5 shrink-0"
                                onClick={() => retirerRepas(repas.id)}
                              >
                                <X className="h-3 w-3" />
                              </Button>
                            </div>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 w-full text-xs"
                              onClick={() => ouvrirDialogue(date, valeur)}
                            >
                              <Plus className="h-3 w-3 mr-1" />
                              Ajouter
                            </Button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Dialogue ajout repas */}
      <Dialog open={dialogueOuvert} onOpenChange={setDialogueOuvert}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ajouter un repas</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {repasEnCours && (
              <p className="text-sm text-muted-foreground">
                {JOURS[datesSemaine.indexOf(repasEnCours.date)]}{" "}
                {new Date(repasEnCours.date).toLocaleDateString("fr-FR", {
                  day: "numeric",
                  month: "long",
                })}{" "}
                — {TYPES_REPAS.find((t) => t.valeur === repasEnCours.type_repas)?.label}
              </p>
            )}
            <div className="space-y-2">
              <Label htmlFor="notes-repas">Notes / Plat</Label>
              <Input
                id="notes-repas"
                value={notesRepas}
                onChange={(e) => setNotesRepas(e.target.value)}
                placeholder="Ex: Quiche lorraine"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setDialogueOuvert(false)}
              >
                Annuler
              </Button>
              <Button
                disabled={enAjout || !notesRepas.trim()}
                onClick={() => {
                  if (repasEnCours) {
                    ajouterRepas({
                      date: repasEnCours.date,
                      type_repas: repasEnCours.type_repas,
                      notes: notesRepas,
                    });
                  }
                }}
              >
                {enAjout && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Ajouter
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
