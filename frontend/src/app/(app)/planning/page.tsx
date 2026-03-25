// ═══════════════════════════════════════════════════════════
// Planning — Calendrier repas de la semaine
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo } from "react";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Plus,
  Trash2,
  Sparkles,
  Clock,
  Download,
} from "lucide-react";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import {
  obtenirPlanningSemaine,
  definirRepas,
  supprimerRepas,
  genererPlanningSemaine,
  exporterPlanningIcal,
  obtenirNutritionHebdo,
} from "@/bibliotheque/api/planning";
import type { TypeRepas, CreerRepasPlanningDTO, RepasPlanning } from "@/types/planning";
import { toast } from "sonner";

const JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"];

const TYPES_REPAS: { value: TypeRepas; label: string }[] = [
  { value: "petit_dejeuner", label: "Petit-déj" },
  { value: "dejeuner", label: "Déjeuner" },
  { value: "gouter", label: "Goûter" },
  { value: "diner", label: "Dîner" },
];

function getLundiSemaine(offset: number): string {
  const d = new Date();
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1) + offset * 7;
  const lundi = new Date(d.setDate(diff));
  return lundi.toISOString().split("T")[0];
}

function formatDateJour(dateStr: string, indexJour: number): string {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + indexJour);
  return d.toISOString().split("T")[0];
}

export default function PagePlanning() {
  const [semaineOffset, setSemaineOffset] = useState(0);
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [jourSelectionne, setJourSelectionne] = useState(0);
  const [typeRepas, setTypeRepas] = useState<TypeRepas>("dejeuner");
  const [notesRepas, setNotesRepas] = useState("");

  const dateDebut = getLundiSemaine(semaineOffset);
  const invalider = utiliserInvalidation();

  const { data: planning, isLoading } = utiliserRequete(
    ["planning", "semaine", dateDebut],
    () => obtenirPlanningSemaine(dateDebut)
  );

  const { data: nutrition } = utiliserRequete(
    ["planning", "nutrition", dateDebut],
    () => obtenirNutritionHebdo(dateDebut)
  );

  const mutationAjouter = utiliserMutation(
    (dto: CreerRepasPlanningDTO) => definirRepas(dto),
    {
      onSuccess: () => {
        invalider(["planning", "semaine", dateDebut]);
        setDialogOuvert(false);
        setNotesRepas("");
        toast.success("Repas ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const mutationSupprimer = utiliserMutation(
    (id: number) => supprimerRepas(id),
    {
      onSuccess: () => { invalider(["planning", "semaine", dateDebut]); toast.success("Repas retiré"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const mutationGenerer = utiliserMutation(
    (_: void) => genererPlanningSemaine(),
    {
      onSuccess: () => { invalider(["planning", "semaine", dateDebut]); toast.success("Planning généré"); },
      onError: () => toast.error("Erreur lors de la génération"),
    }
  );

  // Grouper les repas par jour
  const repasParJour = useMemo(() => {
    const map: Record<string, RepasPlanning[]> = {};
    if (planning?.repas) {
      for (const repas of planning.repas) {
        const dateKey = repas.date?.split("T")[0] ?? "";
        if (!map[dateKey]) map[dateKey] = [];
        map[dateKey].push(repas);
      }
    }
    return map;
  }, [planning]);

  function ouvrirAjout(indexJour: number) {
    setJourSelectionne(indexJour);
    setTypeRepas("dejeuner");
    setNotesRepas("");
    setDialogOuvert(true);
  }

  function ajouterRepas() {
    const dateRepas = formatDateJour(dateDebut, jourSelectionne);
    mutationAjouter.mutate({
      date: dateRepas,
      type_repas: typeRepas,
      notes: notesRepas || undefined,
    });
  }

  const dateLundi = new Date(dateDebut);
  const dateDimanche = new Date(dateDebut);
  dateDimanche.setDate(dateDimanche.getDate() + 6);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📅 Planning</h1>
          <p className="text-muted-foreground">
            Planning des repas de la semaine
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/planning/timeline">
            <Button variant="outline" size="sm">
              <Clock className="mr-2 h-4 w-4" />
              Timeline
            </Button>
          </Link>
          <Button
            variant="outline"
            size="sm"
            onClick={() => mutationGenerer.mutate(undefined as unknown as void)}
            disabled={mutationGenerer.isPending}
          >
            <Sparkles className="mr-2 h-4 w-4" />
            {mutationGenerer.isPending ? "Génération..." : "IA"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => exporterPlanningIcal(2).catch(() => toast.error("Erreur d'export"))}
            title="Exporter le planning en iCalendar (Google Calendar, Apple Calendar...)"
          >
            <Download className="mr-2 h-4 w-4" />
            iCal
          </Button>
        </div>
      </div>

      {/* Navigation semaine */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSemaineOffset((o) => o - 1)}
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div className="text-center">
          <p className="font-medium">
            {dateLundi.toLocaleDateString("fr-FR", {
              day: "numeric",
              month: "short",
            })}{" "}
            —{" "}
            {dateDimanche.toLocaleDateString("fr-FR", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </p>
          {semaineOffset !== 0 && (
            <button
              className="text-xs text-primary underline"
              onClick={() => setSemaineOffset(0)}
            >
              Revenir à cette semaine
            </button>
          )}
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSemaineOffset((o) => o + 1)}
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>

      {/* Grille semaine */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
          {JOURS.map((j) => (
            <Skeleton key={j} className="h-48" />
          ))}
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7">
          {JOURS.map((jour, i) => {
            const dateJour = formatDateJour(dateDebut, i);
            const repasDuJour = repasParJour[dateJour] ?? [];
            const estAujourdhui =
              dateJour === new Date().toISOString().split("T")[0];

            return (
              <Card
                key={jour}
                className={estAujourdhui ? "border-primary ring-1 ring-primary/30" : ""}
              >
                <CardHeader className="py-2 px-3">
                  <CardTitle className="text-xs flex items-center justify-between">
                    <span className={estAujourdhui ? "text-primary font-bold" : ""}>
                      {jour}
                    </span>
                    <span className="text-muted-foreground font-normal">
                      {new Date(dateJour).getDate()}
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="px-3 pb-3 space-y-1.5 min-h-[120px]">
                  {repasDuJour.map((repas) => (
                    <div
                      key={repas.id}
                      className="flex items-start justify-between gap-1 rounded bg-accent/50 p-1.5 text-xs group"
                    >
                      <div>
                        <Badge variant="outline" className="text-[10px] mb-0.5">
                          {TYPES_REPAS.find((t) => t.value === repas.type_repas)?.label ??
                            repas.type_repas}
                        </Badge>
                        <p className="font-medium">
                          {repas.recette_nom || repas.notes || "—"}
                        </p>
                      </div>
                      <button
                        className="opacity-0 group-hover:opacity-100 text-destructive"
                        onClick={() => mutationSupprimer.mutate(repas.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                  <button
                    className="w-full flex items-center justify-center gap-1 rounded border border-dashed py-1 text-xs text-muted-foreground hover:bg-accent transition-colors"
                    onClick={() => ouvrirAjout(i)}
                  >
                    <Plus className="h-3 w-3" />
                    Ajouter
                  </button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Analyse nutritionnelle hebdo */}
      {nutrition && nutrition.totaux.calories > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Nutrition de la semaine</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="text-center rounded-md bg-orange-50 dark:bg-orange-950/20 p-2">
                <p className="text-2xl font-bold text-orange-600">{nutrition.totaux.calories}</p>
                <p className="text-xs text-muted-foreground">kcal total</p>
              </div>
              <div className="text-center rounded-md bg-blue-50 dark:bg-blue-950/20 p-2">
                <p className="text-2xl font-bold text-blue-600">{nutrition.totaux.proteines}g</p>
                <p className="text-xs text-muted-foreground">Protéines</p>
              </div>
              <div className="text-center rounded-md bg-yellow-50 dark:bg-yellow-950/20 p-2">
                <p className="text-2xl font-bold text-yellow-600">{nutrition.totaux.glucides}g</p>
                <p className="text-xs text-muted-foreground">Glucides</p>
              </div>
              <div className="text-center rounded-md bg-green-50 dark:bg-green-950/20 p-2">
                <p className="text-2xl font-bold text-green-600">{nutrition.totaux.lipides}g</p>
                <p className="text-xs text-muted-foreground">Lipides</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              Moy. {nutrition.moyenne_calories_par_jour} kcal/jour
              {nutrition.nb_repas_sans_donnees > 0 && (
                <span> · {nutrition.nb_repas_sans_donnees} repas sans données</span>
              )}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Dialog ajout repas */}
      <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Ajouter un repas — {JOURS[jourSelectionne]}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <Select
              value={typeRepas}
              onValueChange={(v) => setTypeRepas(v as TypeRepas)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TYPES_REPAS.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              placeholder="Notes (ex: Pâtes carbonara)"
              value={notesRepas}
              onChange={(e) => setNotesRepas(e.target.value)}
            />
            <Button
              onClick={ajouterRepas}
              disabled={mutationAjouter.isPending}
              className="w-full"
            >
              {mutationAjouter.isPending ? "Ajout..." : "Ajouter"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
