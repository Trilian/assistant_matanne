// ═══════════════════════════════════════════════════════════
// Planning Repas — Grille hebdomadaire unifiée
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo, useCallback, useEffect, useRef, lazy, Suspense, type ReactNode } from "react";
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Plus,
  X,
  Loader2,
  Download,
  Search,
  Clock,
  ShoppingCart,
  CookingPot,
  CalendarDays,
  GripVertical,
  Wifi,
  WifiOff,
  Users,
  AlertTriangle,
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
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/composants/ui/sheet";
import { Input } from "@/composants/ui/input";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/composants/ui/tabs";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  obtenirPlanningSemaine,
  obtenirPlanningMensuel,
  obtenirConflitsPlanning,
  definirRepas,
  supprimerRepas,
  genererPlanningSemaine,
  validerPlanning,
  regenererPlanning,
  exporterPlanningIcal,
  exporterPlanningPdf,
  obtenirNutritionHebdo,
  obtenirSuggestionsRapides,
  type ResultatGenerationPlanning,
} from "@/bibliotheque/api/planning";
import { toast } from "sonner";
import { genererCoursesDepuisPlanning, type GenererCoursesResult } from "@/bibliotheque/api/courses";
import { envoyerPlanningTelegram } from "@/bibliotheque/api/telegram";
import { genererSessionDepuisPlanning } from "@/bibliotheque/api/batch-cooking";
import type { GenererSessionDepuisPlanningResult } from "@/types/batch-cooking";
import type {
  TypeRepas,
  RepasPlanning,
  CreerRepasPlanningDTO,
  SuggestionRecettePlanning,
} from "@/types/planning";
import { BadgeNutriscore } from "@/composants/cuisine/badge-nutriscore";
import { CarteModeInvites } from "@/composants/cuisine/carte-mode-invites";
import { ConvertisseurInline } from "@/composants/cuisine/convertisseur-inline";
import { CalendrierMensuel } from "@/composants/planning/calendrier-mensuel";
import { CalendrierMosaiqueRepas } from "@/composants/planning/calendrier-mosaique-repas";
import { CalendrierColonnesPlanning } from "@/composants/planning/calendrier-colonnes-planning";
import { utiliserModeInvites } from "@/crochets/utiliser-mode-invites";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import { utiliserWebSocket } from "@/crochets/utiliser-websocket";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { listerEvenementsFamiliaux } from "@/bibliotheque/api/famille";
import { listerEvenements } from "@/bibliotheque/api/calendriers";
import { obtenirFluxCuisine } from "@/bibliotheque/api/ia-bridges";
import {
  analyserVarietePlanningRepas,
  optimiserNutritionPlanningRepas,
  suggererSimplificationPlanningRepas,
  type AnalyseVarieteResponse,
  type OptimisationNutritionPlanningResponse,
  type SimplificationPlanningResponse,
} from "@/bibliotheque/api/ia-modules";
import { useIsMobile } from "@/crochets/use-mobile";
import { utiliserStockageLocal } from "@/crochets/utiliser-stockage-local";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  closestCenter,
  DndContext,
  DragOverlay,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { CSS } from "@dnd-kit/utilities";

const ContenuNutritionLazy = lazy(() => import("../nutrition/page"));
const ContenuMaSemaineLazy = lazy(() => import("../ma-semaine/page"));

// Noms des jours indexés 0=Dimanche … 6=Samedi (aligné sur Date.getDay())
const NOMS_JOURS_SEMAINE = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"];

// Construit le tableau ordonné de 7 jours à partir d'un jour de début (0-6)
function construireJoursOrdonnes(jourDebut: number): string[] {
  return Array.from({ length: 7 }, (_, i) => NOMS_JOURS_SEMAINE[(jourDebut + i) % 7]);
}
const STAGGER_DELAYS = ["delay-0", "delay-75", "delay-150", "delay-200", "delay-300", "delay-500", "delay-700"];
const TYPES_REPAS: { valeur: TypeRepas; label: string; emoji: string }[] = [
  { valeur: "petit_dejeuner", label: "Petit-déj", emoji: "🌅" },
  { valeur: "dejeuner", label: "Déjeuner", emoji: "☀️" },
  { valeur: "gouter", label: "Goûter", emoji: "🍪" },
  { valeur: "diner", label: "Dîner", emoji: "🌙" },
];

type AnalysePlanningIaResultat = {
  variete: AnalyseVarieteResponse;
  nutrition: OptimisationNutritionPlanningResponse;
  simplification: SimplificationPlanningResponse;
};

function ResponsiveOverlay({
  open,
  onOpenChange,
  title,
  children,
  contentClassName,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  children: ReactNode;
  contentClassName?: string;
}) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent
          side="bottom"
          className={`max-h-[92vh] overflow-y-auto rounded-t-3xl border-x-0 border-b-0 px-0 ${contentClassName ?? ""}`}
        >
          <SheetHeader className="pb-2">
            <SheetTitle>{title}</SheetTitle>
          </SheetHeader>
          <div className="px-4 pb-4">{children}</div>
        </SheetContent>
      </Sheet>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={contentClassName}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {children}
      </DialogContent>
    </Dialog>
  );
}

/**
 * Retourne la date du premier jour de la semaine courante + offset semaines.
 * @param offset  décalage de semaines (0 = semaine en cours)
 * @param jourDebut  0=Dimanche, 1=Lundi … 6=Samedi
 */
function getDebutDeSemaine(offset: number, jourDebut: number): string {
  const now = new Date();
  const jour = now.getDay(); // 0=dim, 1=lun …
  // Nombre de jours à soustraire pour revenir au jour de début voulu
  let diff = ((jour - jourDebut + 7) % 7);
  // Si diff === 0 on est pile le bon jour, aucun recul
  const debut = new Date(now);
  debut.setDate(now.getDate() - diff + offset * 7);
  return debut.toISOString().split("T")[0];
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

function construireIdCasePlanning(date: string, type: TypeRepas): string {
  return `case::${date}::${type}`;
}

function construireIdRepasPlanning(repasId: number): string {
  return `repas::${repasId}`;
}

function CarteRepasDraggable({
  repas,
  label,
  onRetirer,
}: {
  repas: RepasPlanning;
  label: string;
  onRetirer: (repas: RepasPlanning) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: construireIdRepasPlanning(repas.id),
    data: { repasId: repas.id },
  });
  const carteRef = useRef<HTMLDivElement | null>(null);

  const definirRefs = useCallback(
    (node: HTMLDivElement | null) => {
      setNodeRef(node);
      carteRef.current = node;
    },
    [setNodeRef]
  );

  useEffect(() => {
    if (!carteRef.current) {
      return;
    }

    carteRef.current.style.transform = transform ? (CSS.Translate.toString(transform) ?? "") : "";
  }, [transform]);

  return (
    <div
      ref={definirRefs}
      className={`flex items-center justify-between gap-1 rounded-md bg-background/80 ${isDragging ? "opacity-60 shadow-lg ring-2 ring-primary/30" : ""}`}
    >
      <div className="flex items-center gap-1 min-w-0 flex-1">
        <button
          type="button"
          className="rounded p-0.5 text-muted-foreground hover:bg-muted touch-none"
          aria-label={`Déplacer ${repas.recette_nom || repas.notes || label}`}
          {...listeners}
          {...attributes}
        >
          <GripVertical className="h-3 w-3" />
        </button>
        {repas.recette_id ? (
          <a
            href={`/cuisine/recettes/${repas.recette_id}`}
            className="font-medium text-foreground truncate hover:underline hover:text-primary transition-colors"
            title={`Voir la recette : ${repas.recette_nom || repas.notes || "—"}`}
            onClick={(e) => e.stopPropagation()}
          >
            {repas.recette_nom || repas.notes || "—"}
          </a>
        ) : (
          <span className="font-medium text-foreground truncate">
            {repas.recette_nom || repas.notes || "—"}
          </span>
        )}
        {repas.nutri_score && <BadgeNutriscore grade={repas.nutri_score} />}
      </div>
      <div className="flex items-center gap-0.5 shrink-0">
        <ConvertisseurInline className="h-5 px-1" />
        <Button
          asChild
          variant="ghost"
          size="icon"
          className="h-5 w-5"
          title="Lancer un minuteur lié à ce repas"
        >
          <a
            href={`/outils/minuteur?repas=${encodeURIComponent(
              repas.recette_nom || repas.notes || label
            )}&duree=${repas.type_repas === "diner" ? 35 : repas.type_repas === "dejeuner" ? 30 : 15}`}
            aria-label="Ouvrir le minuteur pour ce repas"
          >
            <Clock className="h-3 w-3" />
          </a>
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-5 w-5"
          onClick={() => onRetirer(repas)}
          aria-label="Retirer le repas"
        >
          <X className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}

function CaseRepasPlanning({
  date,
  type,
  label,
  emoji,
  repas,
  repasGlisse,
  onAjouter,
  onRetirer,
}: {
  date: string;
  type: TypeRepas;
  label: string;
  emoji: string;
  repas?: RepasPlanning;
  repasGlisse: RepasPlanning | null;
  onAjouter: (date: string, type: TypeRepas) => void;
  onRetirer: (repas: RepasPlanning) => void;
}) {
  const { isOver, setNodeRef } = useDroppable({
    id: construireIdCasePlanning(date, type),
    data: { date, type },
  });

  const dateSource = (repasGlisse?.date_repas || repasGlisse?.date || "").split("T")[0];
  const estCibleDrop = Boolean(repasGlisse) && !(dateSource === date && repasGlisse?.type_repas === type);

  return (
    <div
      ref={setNodeRef}
      className={`min-h-[48px] rounded-md border border-dashed p-2 text-xs transition-colors ${
        isOver || estCibleDrop ? "border-primary/50 bg-primary/5" : "border-muted-foreground/25"
      }`}
    >
      <div className="text-muted-foreground mb-1">
        {emoji} {label}
      </div>
      {repas ? (
        <CarteRepasDraggable repas={repas} label={label} onRetirer={onRetirer} />
      ) : (
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-full text-xs"
          onClick={() => onAjouter(date, type)}
        >
          <Plus className="h-3 w-3 mr-1" />
          Ajouter
        </Button>
      )}
    </div>
  );
}

export default function PagePlanning() {
  const [vuePlanning, setVuePlanning] = useState<"planning" | "ma-semaine" | "nutrition">("planning");
  const { contexte: modeInvites, mettreAJour: mettreAJourModeInvites, reinitialiser: reinitialiserModeInvites } = utiliserModeInvites();
  const { utilisateur } = utiliserAuth();
  const [modeAffichage, setModeAffichage] = useState<"semaine" | "mois">("semaine");
  const [offsetSemaine, setOffsetSemaine] = useState(0);
  const [offsetMois, setOffsetMois] = useState(0);
  const [dialogueOuvert, setDialogueOuvert] = useState(false);
  const [repasEnCours, setRepasEnCours] = useState<{
    date: string;
    type_repas: TypeRepas;
  } | null>(null);
  const [notesRepas, setNotesRepas] = useState("");
  const [ongletDialogue, setOngletDialogue] = useState<"suggestions" | "libre">("suggestions");
  const [rechercheRecette, setRechercheRecette] = useState("");
  const [coursesDialogue, setCoursesDialogue] = useState(false);
  const [coursesResultat, setCoursesResultat] = useState<GenererCoursesResult | null>(null);
  const [batchDialogue, setBatchDialogue] = useState(false);
  const [batchResultat, setBatchResultat] = useState<GenererSessionDepuisPlanningResult | null>(null);
  const [choixModePrepa, setChoixModePrepa] = useState(false);
  const [repasGlisse, setRepasGlisse] = useState<RepasPlanning | null>(null);
  const [analysePlanningIa, setAnalysePlanningIa] = useState<AnalysePlanningIaResultat | null>(null);
  const [vuesSupplementairesOuvertes, setVuesSupplementairesOuvertes] = utiliserStockageLocal<boolean>("planning.vuesSupplementaires", false);
  // Jour de début de semaine persisté en localStorage (0=Dim, 1=Lun … 6=Sam)
  const [jourDebutSemaine, setJourDebutSemaine] = utiliserStockageLocal<number>("planning.jourDebutSemaine", 1);
  const [nbPersonnesBase, setNbPersonnesBase] = utiliserStockageLocal<number>("planning.nbPersonnes", 2);
  // Panneau invités : ouvert uniquement si l'utilisateur l'active, fermé par défaut
  const [panneauInvitesOuvert, setPanneauInvitesOuvert] = utiliserStockageLocal<boolean>("planning.panneauInvites", false);
  // Message d'erreur IA affiché sous le bouton "Générer IA" (plus fiable qu'un toast)
  const [erreurIA, setErreurIA] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 6,
      },
    })
  );

  const invalider = utiliserInvalidation();
  const { planifierSuppression } = utiliserSuppressionAnnulable({ ttlMs: 8000 });
  const dateDebut = getDebutDeSemaine(offsetSemaine, jourDebutSemaine);
  const datesSemaine = getDatesDeSemaine(dateDebut);
  const moisDate = new Date();
  moisDate.setMonth(moisDate.getMonth() + offsetMois);
  const moisSelectionne = `${moisDate.getFullYear()}-${String(moisDate.getMonth() + 1).padStart(2, "0")}`;
  const jours = construireJoursOrdonnes(jourDebutSemaine);
  const identifiantPresencePlanning = String(utilisateur?.id ?? utilisateur?.email ?? "planning-local");
  const nomPresencePlanning = String(utilisateur?.nom ?? "Membre du foyer");
  const baseWsPlanning = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/^http/, "ws");
  const salonPlanningId = Number(dateDebut.replaceAll("-", ""));
  const {
    connecte: synchroPlanningActive,
    utilisateurs: participantsPlanning,
    envoyer: diffuserPlanning,
    mode: modeSynchroPlanning,
  } = utiliserWebSocket({
    url: `${baseWsPlanning}/api/v1/ws/planning/${salonPlanningId}?user=${encodeURIComponent(identifiantPresencePlanning)}&username=${encodeURIComponent(nomPresencePlanning)}`,
    gestionnaires: {
      repas_added: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
          invalider(["planning", "nutrition"]);
        }
      },
      repas_updated: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
          invalider(["planning", "nutrition"]);
        }
      },
      repas_removed: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
          invalider(["planning", "nutrition"]);
        }
      },
      slot_swapped: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
        }
      },
    },
    maxTentatives: 3,
  });

  // ─── Requêtes ───
  const { data: planning, isLoading } = utiliserRequete(
    ["planning", dateDebut],
    () => obtenirPlanningSemaine(dateDebut)
  );

  const { data: planningMensuel, isLoading: chargementMensuel } = utiliserRequete(
    ["planning", "mensuel", moisSelectionne],
    () => obtenirPlanningMensuel(moisSelectionne),
    { enabled: modeAffichage === "mois" }
  );

  const { data: conflits } = utiliserRequete(
    ["planning", "conflits", dateDebut],
    () => obtenirConflitsPlanning(dateDebut),
    { staleTime: 3 * 60 * 1000 }
  );

  const { data: nutrition } = utiliserRequete(
    ["planning", "nutrition", dateDebut],
    () => obtenirNutritionHebdo(dateDebut)
  );

  const { data: suggestions, isLoading: chargeSuggestions } = utiliserRequete(
    ["planning", "suggestions", repasEnCours?.type_repas ?? "diner"],
    () => obtenirSuggestionsRapides(repasEnCours?.type_repas ?? "diner", 8),
    { enabled: dialogueOuvert }
  );

  const { data: evenementsFamille } = utiliserRequete(
    ["famille", "evenements", "planning-invites"],
    () => listerEvenementsFamiliaux(),
    { staleTime: 10 * 60 * 1000 }
  );

  const { data: evenementsCalendrier } = utiliserRequete(
    ["calendriers", "evenements", "planning-invites"],
    () => {
      const debut = new Date().toISOString().slice(0, 10);
      const fin = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        .toISOString()
        .slice(0, 10);
      return listerEvenements({ date_debut: debut, date_fin: fin });
    },
    { staleTime: 10 * 60 * 1000 }
  );

  const { data: fluxCuisine } = utiliserRequete(
    ["flux", "cuisine", planning?.planning_id ? String(planning.planning_id) : "courant"],
    () => obtenirFluxCuisine(planning?.planning_id),
    { staleTime: 30 * 1000 }
  );

  const contexteInvitesActif = modeInvites.actif && modeInvites.nbInvites > 0;
  const evenementsModeInvites = useMemo(() => {
    const items = [...modeInvites.evenements];
    if (modeInvites.occasion.trim()) {
      items.unshift(modeInvites.occasion.trim());
    }
    return Array.from(new Set(items.filter(Boolean))).slice(0, 6);
  }, [modeInvites.evenements, modeInvites.occasion]);

  const suggestionsInvites = useMemo(() => {
    const libellesFamille = (evenementsFamille ?? []).map((item) => item.titre).filter(Boolean);
    const libellesCalendrier = (evenementsCalendrier ?? []).map((item) => item.titre).filter(Boolean);
    return Array.from(new Set([...libellesFamille, ...libellesCalendrier])).slice(0, 6);
  }, [evenementsCalendrier, evenementsFamille]);

  // ─── Mutations ───
  const { mutate: ajouterRepas, isPending: enAjout } = utiliserMutation(
    (dto: CreerRepasPlanningDTO) => definirRepas(dto),
    {
      onSuccess: (_resultat, dto) => {
        invalider(["planning"]);
        setDialogueOuvert(false);
        setNotesRepas("");
        diffuserPlanning({
          action: "repas_added",
          data: { date: dto.date, type_repas: dto.type_repas },
        });
        toast.success("Repas ajouté");
      },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: confirmerSuppressionRepas } = utiliserMutation((repas: RepasPlanning) => supprimerRepas(repas.id), {
    onSuccess: (_resultat, repas) => {
      invalider(["planning"]);
      diffuserPlanning({
        action: "repas_removed",
        data: { repas_id: repas.id, date: repas.date_repas || repas.date, type_repas: repas.type_repas },
      });
      toast.success("Repas retiré");
    },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  const retirerRepas = useCallback(
    (repas: RepasPlanning) => {
      const libelle = repas.recette_nom || repas.notes || `${repas.type_repas} du ${repas.date_repas || repas.date}`;
      planifierSuppression(`repas-${repas.id}`, {
        libelle,
        onConfirmer: () => confirmerSuppressionRepas(repas),
        onErreur: () => toast.error("Erreur lors de la suppression"),
      });
    },
    [confirmerSuppressionRepas, planifierSuppression]
  );

  const toastIaRef = useRef<string | number | null>(null);

  const { mutate: genererIA, isPending: enGeneration } = utiliserMutation(
    () =>
      genererPlanningSemaine({
        date_debut: dateDebut,
        nb_personnes: nbPersonnesBase + (contexteInvitesActif ? modeInvites.nbInvites : 0),
        preferences:
          contexteInvitesActif || evenementsModeInvites.length > 0
            ? {
                mode_invites: contexteInvitesActif,
                nb_invites: contexteInvitesActif ? modeInvites.nbInvites : 0,
                occasion: modeInvites.occasion || undefined,
                evenements: evenementsModeInvites,
              }
            : undefined,
      }),
    {
      onSuccess: async (resultat: ResultatGenerationPlanning) => {
        if (toastIaRef.current !== null) {
          toast.dismiss(toastIaRef.current);
          toastIaRef.current = null;
        }
        invalider(["planning"]);

        if (!resultat.genere_par_ia) {
          const msg = "Le planning a été créé sans IA. Réessayez ou vérifiez la clé Mistral.";
          setErreurIA(msg);
          toast.error(msg, { duration: 8000 });
        } else {
          setErreurIA(null);
          toast.success("Planning généré par l'IA !", { duration: 5000 });
        }

        if (resultat?.planning_id) {
          try {
            await envoyerPlanningTelegram(resultat.planning_id);
          } catch {
            // Ne bloque pas le flux principal si Telegram échoue.
            if (resultat.genere_par_ia) {
              toast.info("Planning généré, notification Telegram non envoyée.");
            }
          }
        }
      },
      onError: (erreur) => {
        if (toastIaRef.current !== null) {
          toast.dismiss(toastIaRef.current);
          toastIaRef.current = null;
        }
        // Le backend a peut-être quand même créé le planning (timeout Axios côté client
        // avant que le serveur réponde) — on invalide pour récupérer le nouveau brouillon.
        invalider(["planning"]);
        invalider(["flux", "cuisine"]);
        const detail =
          (erreur as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
        const msg = detail ?? "Erreur lors de la génération IA";
        setErreurIA(msg);
        toast.error(msg, { duration: 6000 });
      },
    }
  );

  const { mutate: genererCourses, isPending: enGenerationCourses } = utiliserMutation(
    () =>
      genererCoursesDepuisPlanning(dateDebut, {
        nbInvites: contexteInvitesActif ? modeInvites.nbInvites : 0,
        evenements: evenementsModeInvites,
        nomListe:
          contexteInvitesActif && modeInvites.occasion
            ? `Courses ${modeInvites.occasion}`
            : undefined,
      }),
    {
      onSuccess: (result) => {
        setCoursesResultat(result);
        setCoursesDialogue(true);
        toast.success(`${result.total_articles} articles ajoutés !`);
      },
      onError: () => toast.error("Erreur lors de la génération des courses"),
    }
  );

  const { mutate: analyserPlanningIA, isPending: enAnalysePlanningIA } = utiliserMutation(
    async () => {
      if (planningPourAnalyseIa.length === 0) {
        throw new Error("Ajoutez au moins un repas sur la semaine avant l'analyse IA.");
      }

      const [variete, nutritionIA, simplification] = await Promise.all([
        analyserVarietePlanningRepas({ planning_repas: planningPourAnalyseIa }),
        optimiserNutritionPlanningRepas({ planning_repas: planningPourAnalyseIa }),
        suggererSimplificationPlanningRepas({
          planning_repas: planningPourAnalyseIa,
          nb_heures_cuisine_max: 4,
        }),
      ]);

      return { variete, nutrition: nutritionIA, simplification };
    },
    {
      onSuccess: (resultat) => {
        setAnalysePlanningIa(resultat);
        toast.success("Analyse IA du planning prête");
      },
      onError: (erreur) => {
        toast.error(erreur instanceof Error ? erreur.message : "Erreur lors de l'analyse IA");
      },
    }
  );

  const { mutate: validerBrouillonPlanning, isPending: enValidationPlanning } = utiliserMutation(
    (planningId: number) => validerPlanning(planningId),
    {
      onSuccess: () => {
        invalider(["planning"]);
        invalider(["flux", "cuisine"]);
        toast.success("Planning validé, vous pouvez confirmer la liste de courses ensuite.");
      },
      onError: () => toast.error("Impossible de valider ce planning"),
    }
  );

  const { mutate: regenererBrouillonPlanning, isPending: enRegenerationPlanning } = utiliserMutation(
    (planningId: number) => regenererPlanning(planningId),
    {
      onSuccess: () => {
        invalider(["planning"]);
        invalider(["flux", "cuisine"]);
        toast.success("Nouveau brouillon généré");
      },
      onError: () => toast.error("Impossible de régénérer le planning"),
    }
  );

  const { mutate: genererBatch, isPending: enGenerationBatch } = utiliserMutation(
    () => {
      if (!planning) throw new Error("Pas de planning");
      if (!planning.planning_id) {
        throw new Error("Planning sans identifiant. Générez d'abord un planning persistant.");
      }
      // Date session = dimanche de cette semaine
      const dimanche = new Date(dateDebut);
      dimanche.setDate(dimanche.getDate() + 6);
      return genererSessionDepuisPlanning({
        planning_id: planning.planning_id,
        date_session: dimanche.toISOString().split("T")[0],
      });
    },
    {
      onSuccess: (result) => {
        setBatchResultat(result);
        setBatchDialogue(true);
        toast.success(`Session batch créée avec ${result.nb_recettes} recettes !`);
      },
      onError: () => toast.error("Erreur lors de la création de la session batch"),
    }
  );

  // ─── Helpers ───
  const repasParJour = useMemo(() => {
    const map: Record<string, RepasPlanning[]> = {};
    if (planning?.repas) {
      for (const r of planning.repas) {
        const key = (r.date_repas || r.date || "").split("T")[0];
        if (!map[key]) map[key] = [];
        map[key].push(r);
      }
    }
    return map;
  }, [planning]);

  const planningPourAnalyseIa = useMemo(() => {
    return datesSemaine
      .map((date, index) => {
        const repasDuJour = repasParJour[date] ?? [];
        const trouverLibelle = (type: TypeRepas) => {
          const repas = repasDuJour.find((item) => item.type_repas === type);
          return repas?.recette_nom || repas?.notes || "";
        };

        return {
          jour: jours[index].toLowerCase(),
          petit_dej: trouverLibelle("petit_dejeuner"),
          midi: trouverLibelle("dejeuner"),
          soir: trouverLibelle("diner"),
        };
      })
      .filter((jour) => Boolean(jour.petit_dej || jour.midi || jour.soir));
  }, [datesSemaine, repasParJour]);

  function trouverRepas(date: string, type: TypeRepas): RepasPlanning | undefined {
    return repasParJour[date]?.find((r) => r.type_repas === type);
  }

  function ouvrirDialogue(date: string, type: TypeRepas) {
    setRepasEnCours({ date, type_repas: type });
    setNotesRepas("");
    setRechercheRecette("");
    setOngletDialogue("suggestions");
    setDialogueOuvert(true);
  }

  const deplacerRepas = useCallback(
    async (dateCible: string, typeCible: TypeRepas, repasSource?: RepasPlanning | null) => {
      const repasActif = repasSource ?? repasGlisse;
      if (!repasActif) return;

      const dateSource = (repasActif.date_repas || repasActif.date || "").split("T")[0];
      if (dateSource === dateCible && repasActif.type_repas === typeCible) {
        setRepasGlisse(null);
        return;
      }

      try {
        await definirRepas({
          date: dateCible,
          type_repas: typeCible,
          recette_id: repasActif.recette_id,
          notes: repasActif.notes ?? repasActif.recette_nom,
          portions: repasActif.portions,
        });

        await supprimerRepas(repasActif.id);
        invalider(["planning"]);
        diffuserPlanning({
          action: "slot_swapped",
          data: {
            repas_id: repasActif.id,
            date_source: dateSource,
            type_source: repasActif.type_repas,
            date_cible: dateCible,
            type_cible: typeCible,
          },
        });
        toast.success("Repas déplacé");
      } catch {
        toast.error("Impossible de déplacer ce repas");
      } finally {
        setRepasGlisse(null);
      }
    },
    [repasGlisse, invalider, diffuserPlanning]
  );

  const handleDragStart = useCallback(
    (event: DragStartEvent) => {
      const repasId = Number(String(event.active.id).replace("repas::", ""));
      const repas = planning?.repas?.find((item) => item.id === repasId) ?? null;
      setRepasGlisse(repas);
    },
    [planning?.repas]
  );

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      const repasId = Number(String(active.id).replace("repas::", ""));
      const repas = planning?.repas?.find((item) => item.id === repasId) ?? repasGlisse;

      if (!over || !repas) {
        setRepasGlisse(null);
        return;
      }

      const [prefixe, dateCible, typeCible] = String(over.id).split("::");
      if (prefixe !== "case" || !dateCible || !typeCible) {
        setRepasGlisse(null);
        return;
      }

      void deplacerRepas(dateCible, typeCible as TypeRepas, repas);
    },
    [deplacerRepas, planning?.repas, repasGlisse]
  );

  const choisirRecette = useCallback(
    (recette: SuggestionRecettePlanning) => {
      if (!repasEnCours) return;
      ajouterRepas({
        date: repasEnCours.date,
        type_repas: repasEnCours.type_repas,
        recette_id: recette.id,
        notes: recette.nom,
      });
    },
    [repasEnCours, ajouterRepas]
  );

  const suggestionsFiltrees = useMemo(() => {
    if (!suggestions) return [];
    if (!rechercheRecette.trim()) return suggestions;
    const q = rechercheRecette.toLowerCase();
    return suggestions.filter(
      (s) =>
        s.nom.toLowerCase().includes(q) ||
        (s.categorie ?? "").toLowerCase().includes(q)
    );
  }, [suggestions, rechercheRecette]);

  const moisLabel = new Date(dateDebut).toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  const moisLabelComplet = moisDate.toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  const resumePeriode =
    modeAffichage === "semaine"
      ? `${moisLabel} · du ${new Date(datesSemaine[0] ?? dateDebut).toLocaleDateString("fr-FR", {
          day: "numeric",
          month: "short",
        })} au ${new Date(datesSemaine[datesSemaine.length - 1] ?? dateDebut).toLocaleDateString("fr-FR", {
          day: "numeric",
          month: "short",
        })}`
      : `Vue mensuelle · ${moisLabelComplet}`;
  const totalCreneauxSemaine = datesSemaine.length * TYPES_REPAS.length;
  const repasPlanifies = planning?.repas?.length ?? 0;
  const creneauxLibres = Math.max(totalCreneauxSemaine - repasPlanifies, 0);
  const caloriesMoyennes = nutrition?.moyenne_calories_par_jour ?? null;
  const nbPersonnes = nbPersonnesBase + (contexteInvitesActif ? modeInvites.nbInvites : 0);
  const statsPlanning = [
    { label: "Repas planifiés", valeur: `${repasPlanifies}/${totalCreneauxSemaine}` },
    { label: "Créneaux libres", valeur: `${creneauxLibres}` },
    { label: "Calories moy.", valeur: caloriesMoyennes ? `${caloriesMoyennes} kcal/j` : "En calcul" },
  ];

  return (
    <div className="space-y-6">
      {/* ─── Onglets haut niveau ─── */}
      <Tabs value={vuePlanning} onValueChange={(v) => setVuePlanning(v as typeof vuePlanning)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="planning">📅 Planning</TabsTrigger>
          <TabsTrigger value="ma-semaine">🔄 Ma Semaine</TabsTrigger>
          <TabsTrigger value="nutrition">🥗 Nutrition</TabsTrigger>
        </TabsList>

        <TabsContent value="ma-semaine" className="mt-4">
          <Suspense fallback={<div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}>
            <ContenuMaSemaineLazy />
          </Suspense>
        </TabsContent>

        <TabsContent value="nutrition" className="mt-4">
          <Suspense fallback={<div className="flex items-center justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>}>
            <ContenuNutritionLazy />
          </Suspense>
        </TabsContent>

        <TabsContent value="planning" className="mt-4 space-y-6">
      {/* ─── En-tête ─── */}
      <Card className="overflow-hidden border-orange-200/70 bg-[linear-gradient(135deg,rgba(255,247,237,0.96),rgba(255,255,255,0.92))] shadow-sm dark:border-orange-900/60 dark:bg-[linear-gradient(135deg,rgba(24,16,10,0.96),rgba(9,14,22,0.94))]">
        <CardContent className="flex flex-col gap-5 p-5">
          {/* ─ Ligne 1 : titre + badges ─ */}
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
                  Invités : +{modeInvites.nbInvites}
                </Badge>
              ) : null}
            </div>
          </div>

          {/* ─ Ligne 2 : stats pleine largeur ─ */}
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
            {/* Personnes — ajustable */}
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
                <p className="text-[10px] text-muted-foreground mt-0.5">dont {modeInvites.nbInvites} invité(s)</p>
              )}
            </div>
          </div>

          {/* ─ Ligne 3 : navigation + actions pleine largeur ─ */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            {/* Navigation temporelle */}
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
                onClick={() => {
                  if (modeAffichage === "semaine") {
                    setOffsetSemaine((o) => o - 1);
                  } else {
                    setOffsetMois((o) => o - 1);
                  }
                }}
                aria-label="Semaine précédente"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setOffsetSemaine(0);
                  setOffsetMois(0);
                }}
                title="Revenir à la semaine en cours"
              >
                Cette semaine
              </Button>
              {/* Sélecteur du jour de début de semaine */}
              <Select
                value={String(jourDebutSemaine)}
                onValueChange={(v) => {
                  setJourDebutSemaine(Number(v));
                  setOffsetSemaine(0);
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
                  {NOMS_JOURS_SEMAINE.map((nom, idx) => (
                    <SelectItem key={idx} value={String(idx)}>
                      Sem. {nom.toLowerCase()}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="icon"
                onClick={() => {
                  if (modeAffichage === "semaine") {
                    setOffsetSemaine((o) => o + 1);
                  } else {
                    setOffsetMois((o) => o + 1);
                  }
                }}
                aria-label="Semaine suivante"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="default"
                size="sm"
                onClick={() => {
                  setErreurIA(null);
                  toastIaRef.current = toast.loading(
                    "Génération du planning en cours… (peut prendre 30 s)",
                    { duration: Infinity }
                  );
                  genererIA(undefined);
                }}
                disabled={enGeneration}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {enGeneration ? "Génération..." : "Générer IA"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (!planning?.planning_id) {
                    toast.error("Planning non persisté: générez un planning avant export PDF");
                    return;
                  }
                  exporterPlanningPdf(planning.planning_id).catch(() => toast.error("Erreur d'export PDF"));
                }}
                title="Exporter en PDF"
              >
                <Download className="mr-2 h-4 w-4" />
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => exporterPlanningIcal(2).catch(() => toast.error("Erreur d'export"))}
                title="Exporter en iCalendar"
              >
                <Download className="mr-2 h-4 w-4" />
                iCal
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => genererCourses(undefined)}
                disabled={enGenerationCourses}
                title="Générer la liste de courses depuis le planning"
              >
                <ShoppingCart className="mr-2 h-4 w-4" />
                {enGenerationCourses ? "Génération..." : "Courses"}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setChoixModePrepa(true)}
                disabled={!planning}
                title="Mode préparation — batch cooking ou jour par jour"
              >
                <CookingPot className="mr-2 h-4 w-4" />
                Préparation
              </Button>
              {/* Bouton mode invités */}
              <Button
                variant={contexteInvitesActif ? "default" : "outline"}
                size="sm"
                onClick={() => setPanneauInvitesOuvert((v) => !v)}
                title="Mode invités — adapter portions, planning et courses"
                className={contexteInvitesActif ? "bg-amber-500 text-white hover:bg-amber-600 border-transparent" : ""}
              >
                <Users className="mr-2 h-4 w-4" />
                Invités
                {contexteInvitesActif && (
                  <span className="ml-1 rounded-full bg-white/30 px-1.5 text-xs font-semibold">
                    +{modeInvites.nbInvites}
                  </span>
                )}
              </Button>
            </div>
          </div>

          {/* Erreur IA — bandeau persistant sous les actions */}
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

      {/* Mode invités — panneau collapsible, caché par défaut */}
      {panneauInvitesOuvert && (
        <CarteModeInvites
          contexte={modeInvites}
          onChange={(patch) => {
            mettreAJourModeInvites(patch);
            // Fermer automatiquement si on désactive le mode
            if (patch.actif === false) setPanneauInvitesOuvert(false);
          }}
          onReset={() => {
            reinitialiserModeInvites();
            setPanneauInvitesOuvert(false);
          }}
          suggestionsEvenements={suggestionsInvites}
          description="Adaptez le nombre de portions, la génération IA et la liste de courses pour une réception ou un repas élargi."
        />
      )}

      {fluxCuisine?.etape_actuelle === "valider_planning" && fluxCuisine.planning && (
        <Card className="border-amber-300 bg-amber-50/60">
          <CardContent className="py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-amber-900">Brouillon planning en attente de validation</p>
              <p className="text-xs text-amber-800/90">
                Validez ce brouillon pour debloquer la generation et la confirmation des courses.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                onClick={() => validerBrouillonPlanning(fluxCuisine.planning!.id)}
                disabled={enValidationPlanning || enRegenerationPlanning}
              >
                {enValidationPlanning ? "Validation..." : "Valider"}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  const cible = document.querySelector("[data-planning-grid]");
                  cible?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
                disabled={enValidationPlanning || enRegenerationPlanning}
              >
                Modifier
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => regenererBrouillonPlanning(fluxCuisine.planning!.id)}
                disabled={enValidationPlanning || enRegenerationPlanning}
              >
                {enRegenerationPlanning ? "Regeneration..." : "Regenerer"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ─── Grille Planning ─── */}
      {modeAffichage === "mois" ? (
        chargementMensuel ? (
          <Skeleton className="h-[520px] w-full" />
        ) : planningMensuel ? (
          <div className="animate-in fade-in slide-in-from-bottom-1 duration-500">
            <CalendrierMensuel mois={planningMensuel.mois} parJour={planningMensuel.par_jour} />
          </div>
        ) : null
      ) : isLoading ? (
        <div className="grid gap-2">
          {Array.from({ length: 7 }).map((_, i) => (
            <Skeleton key={i} className={`h-24 w-full animate-in fade-in slide-in-from-bottom-1 duration-500 ${STAGGER_DELAYS[i % STAGGER_DELAYS.length]}`} />
          ))}
        </div>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
          onDragCancel={() => setRepasGlisse(null)}
        >
          <div className="space-y-2" data-planning-grid>
            <div className="rounded-2xl border border-dashed bg-muted/35 px-3 py-2 text-xs text-muted-foreground">
              <span className="font-medium text-foreground/80">Astuce :</span> utilisez la poignée <GripVertical className="inline h-3 w-3" /> pour déplacer un repas par glisser-déposer, y compris sur mobile.
            </div>
            {datesSemaine.map((date, idx) => {
              const dateObj = new Date(date);
              const estAujourdhui =
                date === new Date().toISOString().split("T")[0];

              return (
                <Card
                  key={date}
                  className={`${estAujourdhui ? "border-primary" : ""} animate-in fade-in slide-in-from-bottom-1 duration-500 ${STAGGER_DELAYS[idx % STAGGER_DELAYS.length]}`}
                >
                  <CardHeader className="py-2 px-4">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium">
                        {jours[idx]}{" "}
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
                      {TYPES_REPAS.map(({ valeur, label, emoji }) => (
                        <CaseRepasPlanning
                          key={valeur}
                          date={date}
                          type={valeur}
                          label={label}
                          emoji={emoji}
                          repas={trouverRepas(date, valeur)}
                          repasGlisse={repasGlisse}
                          onAjouter={ouvrirDialogue}
                          onRetirer={retirerRepas}
                        />
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
          <DragOverlay>
            {repasGlisse ? (
              <div className="rounded-md border bg-background px-3 py-2 text-sm shadow-xl">
                {repasGlisse.recette_nom || repasGlisse.notes || "Repas"}
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      )}

      {modeAffichage === "semaine" && !isLoading && (
        <div className="animate-in fade-in slide-in-from-bottom-1 duration-500 delay-300">
          <button
            type="button"
            onClick={() => setVuesSupplementairesOuvertes(!vuesSupplementairesOuvertes)}
            className="flex w-full items-center justify-between rounded-xl border border-dashed bg-muted/30 px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground"
          >
            <span className="font-medium">Vues supplémentaires — mosaïque &amp; colonnes</span>
            <ChevronDown
              className={`h-4 w-4 shrink-0 transition-transform duration-200 ${
                vuesSupplementairesOuvertes ? "rotate-180" : ""
              }`}
            />
          </button>
          {vuesSupplementairesOuvertes && (
            <div className="mt-3 space-y-4">
              <CalendrierMosaiqueRepas dates={datesSemaine} repasParJour={repasParJour} />
              <CalendrierColonnesPlanning dates={datesSemaine} repasParJour={repasParJour} />
            </div>
          )}
        </div>
      )}

      {conflits && conflits.items.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">⚠️ Conflits détectés</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">{conflits.resume}</p>
            {conflits.items.slice(0, 5).map((conflit, index) => (
              <div key={`${conflit.date_jour}-${index}`} className="rounded-md border p-3">
                <p className="text-sm font-medium">{conflit.message}</p>
                {conflit.suggestion && (
                  <p className="text-xs text-muted-foreground mt-0.5">Suggestion: {conflit.suggestion}</p>
                )}
                <div className="mt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => toast.info("Aide à la résolution rapide bientôt disponible")}
                  >
                    Résoudre rapidement
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {modeAffichage === "semaine" && (
        <Card className="border-violet-200/70 bg-violet-50/40 dark:border-violet-900/50 dark:bg-violet-950/10">
          <CardHeader className="pb-3">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <CardTitle className="text-base">🧠 Analyse IA de la semaine</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Vérifiez en un clic la variété, l'équilibre nutritionnel et la charge cuisine du planning actuel.
                </p>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => analyserPlanningIA(undefined)}
                disabled={enAnalysePlanningIA || planningPourAnalyseIa.length === 0}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {enAnalysePlanningIA ? "Analyse..." : "Analyser la semaine"}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {analysePlanningIa ? (
              <>
                <div className="grid gap-3 md:grid-cols-3">
                  <div className="rounded-lg border bg-background/80 p-3">
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">Variété</p>
                    <p className="mt-1 text-2xl font-bold text-violet-600">{analysePlanningIa.variete.score_variete}/100</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {analysePlanningIa.variete.types_cuisines.length} styles culinaires détectés
                    </p>
                  </div>
                  <div className="rounded-lg border bg-background/80 p-3">
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">Fruits & légumes</p>
                    <p className="mt-1 text-2xl font-bold text-emerald-600">
                      {Math.round(analysePlanningIa.nutrition.fruits_legumes_quota * 100)}%
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">Objectif hebdo estimé</p>
                  </div>
                  <div className="rounded-lg border bg-background/80 p-3">
                    <p className="text-xs uppercase tracking-wide text-muted-foreground">Charge cuisine</p>
                    <p className="mt-1 text-2xl font-bold text-amber-600">
                      {analysePlanningIa.simplification.gain_temps_minutes} min
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Gain potentiel ({analysePlanningIa.simplification.charge_globale})
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Badge variant={analysePlanningIa.variete.proteins_bien_repartis ? "default" : "secondary"}>
                    Protéines {analysePlanningIa.variete.proteins_bien_repartis ? "bien réparties" : "à renforcer"}
                  </Badge>
                  <Badge variant={analysePlanningIa.nutrition.equilibre_fibre ? "default" : "secondary"}>
                    Fibres {analysePlanningIa.nutrition.equilibre_fibre ? "OK" : "à surveiller"}
                  </Badge>
                  <Badge variant="outline">
                    {analysePlanningIa.simplification.nb_recettes_complexes} recette(s) complexes
                  </Badge>
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-lg border bg-background/80 p-3 space-y-2">
                    <p className="text-sm font-semibold">À privilégier</p>
                    <p className="text-xs text-muted-foreground">
                      {analysePlanningIa.nutrition.aliments_a_privilegier.join(" · ") || "RAS"}
                    </p>
                    {analysePlanningIa.variete.recommandations.length > 0 && (
                      <>
                        <p className="text-sm font-semibold pt-1">Idées de variété</p>
                        <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                          {(analysePlanningIa.variete.recommandations ?? []).slice(0, 3).map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                  <div className="rounded-lg border bg-background/80 p-3 space-y-2">
                    <p className="text-sm font-semibold">Charge & simplification</p>
                    <ul className="list-disc pl-5 text-xs text-muted-foreground space-y-1">
                      {(analysePlanningIa.simplification.suggestions_simplification ?? []).slice(0, 3).map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                    {analysePlanningIa.variete.repetitions_problematiques.length > 0 && (
                      <p className="text-xs text-muted-foreground">
                        Répétitions à surveiller : {analysePlanningIa.variete.repetitions_problematiques.join(", ")}
                      </p>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                Lancez l'analyse pour obtenir un score de variété, un bilan nutritionnel et des suggestions de simplification.
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* ─── Nutrition hebdomadaire ─── */}
      {nutrition && nutrition.totaux.calories > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">🥗 Nutrition de la semaine</CardTitle>
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

      {/* ─── Dialogue ajout repas avec sélecteur de recettes ─── */}
      <ResponsiveOverlay
        open={dialogueOuvert}
        onOpenChange={setDialogueOuvert}
        title="Ajouter un repas"
        contentClassName="sm:max-w-lg"
      >
        {repasEnCours && (
          <p className="text-sm text-muted-foreground -mt-2">
            {jours[datesSemaine.indexOf(repasEnCours.date)]}{" "}
            {new Date(repasEnCours.date).toLocaleDateString("fr-FR", {
              day: "numeric",
              month: "long",
            })}{" "}
            — {TYPES_REPAS.find((t) => t.valeur === repasEnCours.type_repas)?.emoji}{" "}
            {TYPES_REPAS.find((t) => t.valeur === repasEnCours.type_repas)?.label}
          </p>
        )}
        <Tabs value={ongletDialogue} onValueChange={(v) => setOngletDialogue(v as "suggestions" | "libre")}>
          <TabsList className="w-full">
            <TabsTrigger value="suggestions" className="flex-1">
              <Search className="h-3.5 w-3.5 mr-1.5" />
              Recettes
            </TabsTrigger>
            <TabsTrigger value="libre" className="flex-1">
              <Plus className="h-3.5 w-3.5 mr-1.5" />
              Texte libre
            </TabsTrigger>
          </TabsList>

          {/* ─── Onglet suggestions de recettes ─── */}
          <TabsContent value="suggestions" className="space-y-3 mt-3">
            <div className="flex gap-2">
              <Input
                placeholder="Rechercher une recette..."
                value={rechercheRecette}
                onChange={(e) => setRechercheRecette(e.target.value)}
                className="flex-1"
              />
              <Button
                variant="outline"
                size="sm"
                title="Surprise du chef — choisit une recette au hasard"
                disabled={!suggestions || suggestions.length === 0 || enAjout}
                onClick={() => {
                  if (!suggestions || suggestions.length === 0) return;
                  const idx = Math.floor(Math.random() * suggestions.length);
                  choisirRecette(suggestions[idx]);
                }}
              >
                🎲
              </Button>
            </div>
            <div className="max-h-64 overflow-y-auto space-y-1.5">
              {chargeSuggestions ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-14 w-full" />
                ))
              ) : suggestionsFiltrees.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-6">
                  Aucune recette trouvée
                </p>
              ) : (
                suggestionsFiltrees.map((recette) => (
                  <button
                    key={recette.id}
                    onClick={() => choisirRecette(recette)}
                    disabled={enAjout}
                    className="w-full flex items-center justify-between rounded-md border p-3 text-left hover:bg-accent transition-colors disabled:opacity-50"
                  >
                    <div className="min-w-0">
                      <p className="font-medium text-sm truncate">{recette.nom}</p>
                      {recette.categorie && (
                        <Badge variant="outline" className="text-[10px] mt-0.5">
                          {recette.categorie}
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 shrink-0 ml-2">
                      {recette.temps_total > 0 && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {recette.temps_total} min
                        </span>
                      )}
                      <ConvertisseurInline />
                    </div>
                  </button>
                ))
              )}
            </div>
          </TabsContent>

          {/* ─── Onglet texte libre ─── */}
          <TabsContent value="libre" className="space-y-4 mt-3">
            <Input
              value={notesRepas}
              onChange={(e) => setNotesRepas(e.target.value)}
              placeholder="Ex: Quiche lorraine"
            />
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
          </TabsContent>
        </Tabs>
      </ResponsiveOverlay>

      {/* ─── Dialogue résultat courses ─── */}
      <ResponsiveOverlay
        open={coursesDialogue}
        onOpenChange={setCoursesDialogue}
        title="🛒 Liste de courses générée"
        contentClassName="sm:max-w-md"
      >
        {coursesResultat && (
          <div className="space-y-4">
            <div className="text-sm space-y-1">
              <p className="font-medium">
                ✅ {coursesResultat.total_articles} articles ajoutés
              </p>
              {coursesResultat.contexte && coursesResultat.contexte.nb_invites > 0 && (
                <p className="text-muted-foreground">
                  👥 Quantités ajustées pour {coursesResultat.contexte.nb_invites} invité(s)
                </p>
              )}
              {coursesResultat.articles_en_stock > 0 && (
                <p className="text-muted-foreground">
                  📦 {coursesResultat.articles_en_stock} articles déjà en stock (non ajoutés)
                </p>
              )}
            </div>
            {Object.keys(coursesResultat.par_rayon).length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Par rayon :</p>
                <div className="grid grid-cols-2 gap-1">
                  {Object.entries(coursesResultat.par_rayon).map(([rayon, count]) => (
                    <div key={rayon} className="flex items-center justify-between text-sm rounded-md bg-muted/50 px-2 py-1">
                      <span className="capitalize truncate">{rayon.replace(/_/g, " ")}</span>
                      <Badge variant="secondary" className="ml-1 text-xs">{count}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setCoursesDialogue(false)}>
                Fermer
              </Button>
              <Button
                onClick={() => {
                  setCoursesDialogue(false);
                  window.location.href = `/cuisine/courses`;
                }}
              >
                Voir la liste
              </Button>
            </div>
          </div>
        )}
      </ResponsiveOverlay>

      {/* ─── Dialogue résultat batch ─── */}
      <ResponsiveOverlay
        open={batchDialogue}
        onOpenChange={setBatchDialogue}
        title="🍳 Session batch créée"
        contentClassName="sm:max-w-md"
      >
        {batchResultat && (
          <div className="space-y-4">
            <div className="text-sm space-y-1">
              <p className="font-medium">
                ✅ {batchResultat.nom}
              </p>
              <p className="text-muted-foreground">
                📖 {batchResultat.nb_recettes} recette{batchResultat.nb_recettes > 1 ? "s" : ""} sélectionnée{batchResultat.nb_recettes > 1 ? "s" : ""}
              </p>
              <p className="text-muted-foreground">
                ⏱️ Durée estimée : {batchResultat.duree_estimee} minutes
              </p>
            </div>
            {(batchResultat.robots_utilises ?? []).length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Robots compatibles :</p>
                <div className="flex flex-wrap gap-1">
                  {batchResultat.robots_utilises.map((robot) => (
                    <Badge key={robot} variant="outline" className="text-xs">
                      {robot}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {(batchResultat.recettes ?? []).length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium">Recettes :</p>
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {batchResultat.recettes.map((r) => (
                    <div
                      key={r.id}
                      className="text-sm rounded-md bg-muted/50 px-2 py-1"
                    >
                      {r.nom} ({r.portions} portions)
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setBatchDialogue(false)}>
                Fermer
              </Button>
              <Button
                onClick={() => {
                  setBatchDialogue(false);
                  window.location.href = `/cuisine/batch-cooking/${batchResultat.session_id}`;
                }}
              >
                Voir la session
              </Button>
            </div>
          </div>
        )}
      </ResponsiveOverlay>
      {/* ─── Dialog choix mode préparation ─── */}
      <ResponsiveOverlay
        open={choixModePrepa}
        onOpenChange={setChoixModePrepa}
        title="🍳 Mode de préparation"
        contentClassName="sm:max-w-md"
      >
        <div className="space-y-3 pt-2">
          <p className="text-sm text-muted-foreground">
            Choisissez comment vous souhaitez préparer les repas de cette semaine.
          </p>

          {/* Option 1 : Batch cooking */}
          <button
            className="w-full text-left rounded-lg border p-4 hover:bg-accent transition-colors group"
            onClick={() => {
              setChoixModePrepa(false);
              genererBatch(undefined);
            }}
            disabled={enGenerationBatch}
          >
            <div className="flex items-start gap-3">
              <div className="rounded-md bg-primary/10 p-2 group-hover:bg-primary/20 transition-colors shrink-0">
                <CookingPot className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-sm">Batch Cooking</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Préparez tout en une seule session le week-end. Idéal pour gagner du temps en semaine.
                </p>
                {enGenerationBatch && (
                  <p className="text-xs text-primary mt-1 flex items-center gap-1">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Génération en cours…
                  </p>
                )}
              </div>
            </div>
          </button>

          {/* Option 2 : Jour par jour */}
          <button
            className="w-full text-left rounded-lg border p-4 hover:bg-accent transition-colors group"
            onClick={() => {
              setChoixModePrepa(false);
              window.location.href = "/cuisine/ma-semaine";
            }}
          >
            <div className="flex items-start gap-3">
              <div className="rounded-md bg-orange-100 dark:bg-orange-900/30 p-2 group-hover:bg-orange-200 dark:group-hover:bg-orange-900/50 transition-colors shrink-0">
                <CalendarDays className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <p className="font-semibold text-sm">Jour par jour</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Suivez le wizard "Ma Semaine" pour préparer chaque jour avec flexibilité.
                </p>
              </div>
            </div>
          </button>
        </div>
      </ResponsiveOverlay>
        </TabsContent>
      </Tabs>
    </div>
  );
}
