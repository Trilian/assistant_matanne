"use client";

import {
  AlertTriangle,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  CookingPot,
  Download,
  Loader2,
  ShoppingCart,
  Sparkles,
  Users,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent } from "@/composants/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";

type ModeAffichage = "semaine" | "mois";

type StatPlanning = {
  label: string;
  valeur: string;
};

type Props = {
  resumePeriode: string;
  synchroPlanningActive: boolean;
  modeSynchroPlanning: string;
  contexteInvitesActif: boolean;
  nbInvites: number;
  statsPlanning: StatPlanning[];
  nbPersonnesBase: number;
  nbPersonnes: number;
  setNbPersonnesBase: (valeur: number) => void;
  modeAffichage: ModeAffichage;
  setModeAffichage: (valeur: ModeAffichage) => void;
  allerPrecedent: () => void;
  reinitialiserPeriode: () => void;
  jourDebutSemaine: number;
  setJourDebutSemaine: (valeur: number) => void;
  setOffsetSemaine: (updater: (valeur: number) => number) => void;
  nomsJoursSemaine: string[];
  allerSuivant: () => void;
  onOuvrirGenerationIa: () => void;
  enGeneration: boolean;
  onExporterPdf: () => void;
  onExporterIcal: () => void;
  onGenererCourses: () => void;
  enGenerationCourses: boolean;
  onOuvrirChoixModePrepa: () => void;
  planningExiste: boolean;
  onTogglePanneauInvites: () => void;
  erreurIA: string | null;
  setErreurIA: (message: string | null) => void;
};

export function EnTetePlanning({
  resumePeriode,
  synchroPlanningActive,
  modeSynchroPlanning,
  contexteInvitesActif,
  nbInvites,
  statsPlanning,
  nbPersonnesBase,
  nbPersonnes,
  setNbPersonnesBase,
  modeAffichage,
  setModeAffichage,
  allerPrecedent,
  reinitialiserPeriode,
  jourDebutSemaine,
  setJourDebutSemaine,
  setOffsetSemaine,
  nomsJoursSemaine,
  allerSuivant,
  onOuvrirGenerationIa,
  enGeneration,
  onExporterPdf,
  onExporterIcal,
  onGenererCourses,
  enGenerationCourses,
  onOuvrirChoixModePrepa,
  planningExiste,
  onTogglePanneauInvites,
  erreurIA,
  setErreurIA,
}: Props) {
  return (
    <Card className="overflow-hidden border-orange-200/70 bg-[linear-gradient(135deg,rgba(255,247,237,0.96),rgba(255,255,255,0.92))] shadow-sm dark:border-orange-900/60 dark:bg-[linear-gradient(135deg,rgba(24,16,10,0.96),rgba(9,14,22,0.94))]">
      <CardContent className="flex flex-col gap-5 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-1.5">
            <h1 className="text-2xl font-bold tracking-tight lg:text-3xl">📅 Planning repas</h1>
            <p className="text-sm leading-6 text-muted-foreground">
              {resumePeriode} — organisez la semaine, gardez la synchro foyer et lancez courses ou préparation depuis un seul écran.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 shrink-0">
            <Badge variant="secondary" className="bg-white/80 text-orange-900 dark:bg-white/10 dark:text-orange-100">
              <CalendarDays className="mr-1 h-3.5 w-3.5" />
              Planification hebdo
            </Badge>
            <Badge variant={synchroPlanningActive ? "default" : modeSynchroPlanning === "polling" ? "secondary" : "outline"}>
              {synchroPlanningActive ? (
                <span className="inline-flex items-center gap-1"><Wifi className="h-3 w-3" /> Synchro live</span>
              ) : (
                <span className="inline-flex items-center gap-1"><WifiOff className="h-3 w-3" /> {modeSynchroPlanning === "polling" ? "Fallback réseau" : "Hors temps réel"}</span>
              )}
            </Badge>
            {contexteInvitesActif ? (
              <Badge variant="outline" className="bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-200">
                Invités : +{nbInvites}
              </Badge>
            ) : null}
          </div>
        </div>

        <div className="grid gap-3 grid-cols-2 sm:grid-cols-4">
          {statsPlanning.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-white/60 bg-white/70 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5"
            >
              <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{stat.label}</p>
              <p className="mt-1 text-xl font-semibold">{stat.valeur}</p>
            </div>
          ))}
          <div className="rounded-2xl border border-white/60 bg-white/70 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5">
            <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Personnes</p>
            <div className="mt-1 flex items-center gap-2">
              <button
                type="button"
                className="flex h-6 w-6 items-center justify-center rounded-full border text-sm leading-none hover:bg-muted"
                onClick={() => setNbPersonnesBase(Math.max(1, nbPersonnesBase - 1))}
                aria-label="Réduire le nombre de personnes"
              >−</button>
              <span className="text-xl font-semibold">{nbPersonnes} pers.</span>
              <button
                type="button"
                className="flex h-6 w-6 items-center justify-center rounded-full border text-sm leading-none hover:bg-muted"
                onClick={() => setNbPersonnesBase(nbPersonnesBase + 1)}
                aria-label="Augmenter le nombre de personnes"
              >+</button>
            </div>
            {contexteInvitesActif && (
              <p className="text-[10px] text-muted-foreground mt-0.5">dont {nbInvites} invité(s)</p>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-1.5">
            <div className="rounded-xl border border-white/60 bg-white/80 p-1 shadow-sm dark:border-white/10 dark:bg-white/5">
              <div className="flex items-center gap-0.5">
                <Button
                  variant={modeAffichage === "semaine" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setModeAffichage("semaine")}
                >
                  Semaine
                </Button>
                <Button
                  variant={modeAffichage === "mois" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setModeAffichage("mois")}
                >
                  Mois
                </Button>
              </div>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={allerPrecedent}
              aria-label="Semaine précédente"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={reinitialiserPeriode}
              title="Revenir à la semaine en cours"
            >
              Cette semaine
            </Button>
            <Select
              value={String(jourDebutSemaine)}
              onValueChange={(v) => {
                setJourDebutSemaine(Number(v));
                setOffsetSemaine((valeur) => valeur - valeur);
              }}
            >
              <SelectTrigger
                size="sm"
                className="h-9 w-auto gap-1 border-white/60 bg-white/80 text-xs dark:border-white/10 dark:bg-white/5"
                title="Changer le jour de début de semaine"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {nomsJoursSemaine.map((nom, idx) => (
                  <SelectItem key={idx} value={String(idx)}>
                    Sem. {nom.toLowerCase()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              onClick={allerSuivant}
              aria-label="Semaine suivante"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              variant="default"
              size="sm"
              onClick={onOuvrirGenerationIa}
              disabled={enGeneration}
            >
              {enGeneration ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="mr-2 h-4 w-4" />
              )}
              {enGeneration ? "Génération en cours…" : "Générer IA"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onExporterPdf}
              title="Exporter en PDF"
            >
              <Download className="mr-2 h-4 w-4" />
              PDF
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onExporterIcal}
              title="Exporter en iCalendar"
            >
              <Download className="mr-2 h-4 w-4" />
              iCal
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onGenererCourses}
              disabled={enGenerationCourses}
              title="Générer la liste de courses depuis le planning"
            >
              <ShoppingCart className="mr-2 h-4 w-4" />
              {enGenerationCourses ? "Génération..." : "Courses"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onOuvrirChoixModePrepa}
              disabled={!planningExiste}
              title="Mode préparation — batch cooking ou jour par jour"
            >
              <CookingPot className="mr-2 h-4 w-4" />
              Préparation
            </Button>
            <Button
              variant={contexteInvitesActif ? "default" : "outline"}
              size="sm"
              onClick={onTogglePanneauInvites}
              title="Mode invités — adapter portions, planning et courses"
              className={contexteInvitesActif ? "bg-amber-500 text-white hover:bg-amber-600 border-transparent" : ""}
            >
              <Users className="mr-2 h-4 w-4" />
              Invités
              {contexteInvitesActif && (
                <span className="ml-1 rounded-full bg-white/30 px-1.5 text-xs font-semibold">
                  +{nbInvites}
                </span>
              )}
            </Button>
          </div>
        </div>

        {erreurIA && (
          <div className="mt-3 flex items-start gap-2 rounded-lg border border-orange-300 bg-orange-50 px-4 py-3 text-sm text-orange-800 dark:border-orange-800 dark:bg-orange-950/30 dark:text-orange-300">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <span className="flex-1">{erreurIA}</span>
            <button
              type="button"
              aria-label="Fermer"
              className="rounded p-0.5 hover:bg-orange-200 dark:hover:bg-orange-800"
              onClick={() => setErreurIA(null)}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
