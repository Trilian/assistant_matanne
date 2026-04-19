// ═══════════════════════════════════════════════════════════
// Détail Session Batch Cooking
// ═══════════════════════════════════════════════════════════

"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState, useMemo } from "react";
import {
  ArrowLeft,
  ChefHat,
  Clock,
  CheckCircle2,
  Circle,
  Bot,
  CalendarDays,
  Loader2,
  Pencil,
  Search,
  Sparkles,
  X,
  ChevronDown,
  ChevronUp,
  LayoutList,
  BarChart3,
  Thermometer,
  Timer,
  UtensilsCrossed,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api";
import { obtenirSessionBatch, modifierSessionBatch, genererEtapesSession } from "@/bibliotheque/api/batch-cooking";
import { listerRecettes } from "@/bibliotheque/api/recettes";
import { utiliserStoreUI } from "@/magasins/store-ui";
import { toast } from "sonner";

const STATUT_LABELS: Record<string, string> = {
  planifie: "Planifiée",
  en_cours: "En cours",
  termine: "Terminée",
  annule: "Annulée",
};

const STATUT_COLORS: Record<string, string> = {
  planifie: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  en_cours: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  termine: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  annule: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

// ─── Constantes robots pour la swimlane ────────────────────────────────────
const ROBOT_LABELS: Record<string, string> = {
  vous: "Vous",
  cookeo: "🍲 Cookeo",
  monsieur_cuisine: "🤖 M. Cuisine",
  airfryer: "🍟 Airfryer",
  multicooker: "♨️ Multicooker",
  four: "🔥 Four",
  plaques: "🍳 Plaques",
};
const ROBOT_COLORS: Record<string, string> = {
  vous: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  cookeo: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  monsieur_cuisine: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  airfryer: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  multicooker: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  four: "bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200",
  plaques: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
};

const ROBOTS_BATCH_OPTIONS = [
  { valeur: "cookeo", label: "🍲 Cookeo" },
  { valeur: "monsieur_cuisine", label: "🤖 M. Cuisine" },
  { valeur: "airfryer", label: "🍟 Airfryer" },
  { valeur: "multicooker", label: "♨️ Multicooker" },
  { valeur: "four", label: "🔥 Four" },
  { valeur: "plaques", label: "🍳 Plaques" },
  { valeur: "robot_patissier", label: "🎂 Robot pâtissier" },
  { valeur: "mixeur", label: "🥤 Mixeur" },
  { valeur: "hachoir", label: "🔪 Hachoir" },
];

function normaliserTrack(robots: string[]): string {
  if (!robots || robots.length === 0) return "vous";
  const raw = robots[0].toLowerCase().replace(/ /g, "_").replace(".", "");
  // Alias connus
  if (raw === "monsieur_cuisine" || raw === "mr_cuisine") return "monsieur_cuisine";
  return raw;
}

interface EtapeBatch {
  id: number;
  ordre: number;
  groupe_parallele?: number | null;
  titre: string;
  duree_minutes?: number | null;
  robots_requis: string[];
  statut: string;
  est_terminee: boolean;
  description?: string | null;
  est_supervision?: boolean;
  temperature?: number | null;
}

function TimelineSwimlane({
  etapes,
  robotsUtilises,
}: {
  etapes: EtapeBatch[];
  robotsUtilises: string[];
}) {
  // Déduire les tracks présents
  const tracksPresents: string[] = ["vous"];
  for (const e of etapes) {
    const track = normaliserTrack(e.robots_requis);
    if (track !== "vous" && !tracksPresents.includes(track)) {
      tracksPresents.push(track);
    }
  }
  // Ajouter robots configurés mais pas encore dans les étapes (pour la cohérence)
  for (const r of robotsUtilises) {
    const track = normaliserTrack([r]);
    if (!tracksPresents.includes(track)) tracksPresents.push(track);
  }

  // Grouper par groupe_parallele (null/undefined → groupe solo unique)
  const groupesMap = new Map<number, EtapeBatch[]>();
  let compteurSolo = 1000; // compteur pour les groupes sans id
  for (const e of [...etapes].sort((a, b) => a.ordre - b.ordre)) {
    const gId = e.groupe_parallele != null ? e.groupe_parallele : compteurSolo++;
    if (!groupesMap.has(gId)) groupesMap.set(gId, []);
    groupesMap.get(gId)!.push(e);
  }
  const groupes = Array.from(groupesMap.entries()).sort((a, b) => {
    const minA = Math.min(...a[1].map((e) => e.ordre));
    const minB = Math.min(...b[1].map((e) => e.ordre));
    return minA - minB;
  });

  const dureeGroupe = (etapes: EtapeBatch[]) =>
    Math.max(...etapes.map((e) => e.duree_minutes ?? 0), 0);

  return (
    <div className="overflow-x-auto -mx-2 px-2">
      <table className="w-full min-w-[480px] border-collapse text-sm">
        <thead>
          <tr>
            <th className="w-16 py-2 pr-3 text-right text-xs text-muted-foreground font-medium">
              Temps
            </th>
            {tracksPresents.map((track) => (
              <th
                key={track}
                className={`px-2 py-2 text-xs font-semibold rounded-t whitespace-nowrap ${
                  ROBOT_COLORS[track] ?? "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                }`}
              >
                {ROBOT_LABELS[track] ?? track}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {groupes.map(([gId, etapesGroupe], idx) => {
            const duree = dureeGroupe(etapesGroupe);
            return (
              <tr key={gId} className={idx % 2 === 0 ? "bg-muted/20" : ""}>
                <td className="py-2 pr-3 text-right align-top">
                  {duree > 0 ? (
                    <span className="flex items-center justify-end gap-0.5 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3 shrink-0" />
                      {duree}&nbsp;min
                    </span>
                  ) : (
                    <span className="text-xs text-muted-foreground">—</span>
                  )}
                </td>
                {tracksPresents.map((track) => {
                  const etape = etapesGroupe.find(
                    (e) => normaliserTrack(e.robots_requis) === track
                  );
                  if (!etape) {
                    return (
                      <td
                        key={track}
                        className="px-2 py-2 text-center text-xs text-muted-foreground/40 border-l border-border/30"
                      >
                        —
                      </td>
                    );
                  }
                  return (
                    <td
                      key={track}
                      className={`px-2 py-2 align-top border-l border-border/30 ${
                        etape.est_supervision
                          ? "border border-dashed border-muted-foreground/30 rounded"
                          : ""
                      } ${etape.est_terminee ? "opacity-50" : ""}`}
                    >
                      <div className="flex flex-col gap-0.5">
                        <span className="font-medium leading-snug">
                          {etape.est_terminee && (
                            <CheckCircle2 className="h-3 w-3 inline mr-1 text-green-500" />
                          )}
                          {etape.titre}
                        </span>
                        {etape.est_supervision && (
                          <span className="text-xs text-muted-foreground flex items-center gap-0.5">
                            <Timer className="h-3 w-3" />
                            Passif
                          </span>
                        )}
                        {etape.temperature != null && (
                          <span className="text-xs text-orange-600 dark:text-orange-400 flex items-center gap-0.5">
                            <Thermometer className="h-3 w-3" />
                            {etape.temperature}°C
                          </span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function PageDetailBatch() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const { definirTitrePage } = utiliserStoreUI();
  const invalider = utiliserInvalidation();

  const [dialogueRecettes, setDialogueRecettes] = useState(false);
  const [recettesSel, setRecettesSel] = useState<number[]>([]);
  const [rechercheRecette, setRechercheRecette] = useState("");
  const [etapesExpandees, setEtapesExpandees] = useState<Set<number>>(new Set());
  const [vueTimeline, setVueTimeline] = useState(false);
  const [robotsSel, setRobotsSel] = useState<string[]>([]);

  function toggleEtape(id: number) {
    setEtapesExpandees((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const { data: session, isLoading } = utiliserRequete(
    ["batch-cooking", String(id)],
    () => obtenirSessionBatch(id),
    { enabled: !isNaN(id) }
  );

  const { data: toutesRecettes, isLoading: chargementRecettes } = utiliserRequete(
    ["recettes", "batch-picker-detail"],
    () => listerRecettes(1, 100),
    { enabled: dialogueRecettes }
  );

  const recettesFiltrees = useMemo(() => {
    const items = toutesRecettes?.items ?? [];
    if (!rechercheRecette.trim()) return items;
    const q = rechercheRecette.toLowerCase();
    return items.filter((r) => r.nom.toLowerCase().includes(q));
  }, [toutesRecettes, rechercheRecette]);

  function ouvrirDialogueRecettes() {
    setRecettesSel(session?.recettes_selectionnees ?? []);
    setRechercheRecette("");
    setDialogueRecettes(true);
  }

  function toggleRecette(rid: number) {
    setRecettesSel((prev) =>
      prev.includes(rid) ? prev.filter((x) => x !== rid) : [...prev, rid]
    );
  }

  const { mutate: sauvegarderRecettes, isPending: enSauvegarde } = utiliserMutation(
    () => modifierSessionBatch(id, { recettes_selectionnees: recettesSel }),
    {
      onSuccess: () => {
        invalider(["batch-cooking"]);
        setDialogueRecettes(false);
        toast.success("Recettes mises à jour");
      },
      onError: () => toast.error("Erreur lors de la mise à jour"),
    }
  );

  const genererEtapesMutation = utiliserMutation(
    () => genererEtapesSession(id),
    {
      onSuccess: () => {
        invalider(["batch-cooking", String(id)]);
        toast.success("Étapes générées avec succès !");
      },
      onError: () => toast.error("Erreur lors de la génération des étapes"),
    }
  );

  async function genererAvecRobots() {
    if (robotsSel.length === 0) {
      toast.error("Sélectionnez au moins un appareil de cuisine");
      return;
    }
    const robotsActuels = session?.robots_utilises ?? [];
    const modifies =
      JSON.stringify([...robotsSel].sort()) !==
      JSON.stringify([...robotsActuels].sort());
    if (modifies) {
      try {
        await modifierSessionBatch(id, { robots_utilises: robotsSel });
      } catch {
        toast.error("Erreur lors de la mise à jour des appareils");
        return;
      }
    }
    genererEtapesMutation.mutate();
  }

  useEffect(() => {
    if (session?.nom) definirTitrePage(session.nom);
    return () => definirTitrePage(null);
  }, [session?.nom, definirTitrePage]);

  // Initialise la sélection de robots depuis la session (une fois au chargement)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (session?.robots_utilises) setRobotsSel(session.robots_utilises);
  }, [session?.id]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Skeleton className="h-9 w-9 rounded-md" />
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour
        </Button>
        <p className="text-muted-foreground">Session introuvable.</p>
      </div>
    );
  }

  const etapes = session.etapes ?? [];
  const etapesTerminees = etapes.filter((e) => e.est_terminee).length;
  const dureeFormatee = session.duree_estimee
    ? `${Math.floor(session.duree_estimee / 60)}h${String(session.duree_estimee % 60).padStart(2, "0")}`
    : null;

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.push("/cuisine/batch-cooking")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-2xl font-bold tracking-tight">{session.nom}</h1>
            <span
              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                STATUT_COLORS[session.statut] ?? "bg-gray-100 text-gray-500"
              }`}
            >
              {STATUT_LABELS[session.statut] ?? session.statut}
            </span>
            {session.avec_jules && (
              <Badge variant="secondary" className="text-xs">
                👦 Avec Jules
              </Badge>
            )}
            {session.genere_par_ia && (
              <Badge variant="outline" className="text-xs">
                ✨ IA
              </Badge>
            )}
          </div>
          {session.date_session && (
            <p className="text-sm text-muted-foreground flex items-center gap-1 mt-0.5">
              <CalendarDays className="h-3.5 w-3.5" />
              {new Date(session.date_session).toLocaleDateString("fr-FR", {
                weekday: "long",
                day: "numeric",
                month: "long",
              })}
            </p>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <ChefHat className="h-8 w-8 text-primary" />
              <div>
                <p className="text-sm text-muted-foreground">Recettes</p>
                <p className="text-3xl font-bold">{session.recettes_selectionnees.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Clock className="h-8 w-8 text-orange-500" />
              <div>
                <p className="text-sm text-muted-foreground">Durée estimée</p>
                <p className="text-3xl font-bold">{dureeFormatee ?? "—"}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Progression</p>
                <p className="text-3xl font-bold">{session.progression}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recettes sélectionnées */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <ChefHat className="h-4 w-4" />
              Recettes sélectionnées ({session.recettes_selectionnees.length})
            </CardTitle>
            <Button variant="outline" size="sm" onClick={ouvrirDialogueRecettes}>
              <Pencil className="h-3.5 w-3.5 mr-1" />
              Modifier
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {session.recettes_selectionnees.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Aucune recette sélectionnée.{" "}
              <button
                className="underline hover:no-underline"
                onClick={ouvrirDialogueRecettes}
              >
                Ajouter des recettes
              </button>
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              {session.recettes_selectionnees.length} recette{session.recettes_selectionnees.length > 1 ? "s" : ""} planifiée{session.recettes_selectionnees.length > 1 ? "s" : ""} pour cette session.
            </p>
          )}
        </CardContent>
      </Card>

      {/* Appareils de cuisine */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Bot className="h-4 w-4" />
            Appareils de cuisine
          </CardTitle>
          <CardDescription>
            Sélectionnez ceux disponibles — l&apos;IA les utilisera pour paralléliser la session
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {ROBOTS_BATCH_OPTIONS.map(({ valeur, label }) => {
              const actif = robotsSel.includes(valeur);
              return (
                <button
                  key={valeur}
                  type="button"
                  onClick={() =>
                    setRobotsSel((prev) =>
                      actif ? prev.filter((r) => r !== valeur) : [...prev, valeur]
                    )
                  }
                  className={`px-2.5 py-1.5 text-xs rounded-md border font-medium transition-colors ${
                    actif
                      ? "bg-primary text-primary-foreground border-primary"
                      : "border-border bg-background hover:bg-accent text-muted-foreground"
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>
          {robotsSel.length === 0 && (
            <p className="mt-2 text-xs text-amber-600 dark:text-amber-400">
              ⚠ Sélectionnez au moins un appareil pour que l&apos;IA puisse planifier la session.
            </p>
          )}
          {robotsSel.length > 1 && (
            <p className="mt-2 text-xs text-green-700 dark:text-green-400">
              ✓ {robotsSel.length} appareils · la session sera parallélisée
            </p>
          )}
        </CardContent>
      </Card>

      {/* Préparer aussi — accompagnements sans recette */}
      {(session.preparations_simples ?? []).length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <UtensilsCrossed className="h-4 w-4" />
              Préparer aussi
            </CardTitle>
            <CardDescription>
              Accompagnements sans recette associée — à préparer en plus lors de cette session
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {(session.preparations_simples ?? []).map((item) => (
                <span
                  key={item}
                  className="inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium"
                >
                  {item}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Étapes */}
      {etapes.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-2 flex-wrap">
              <div>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Loader2 className="h-5 w-5 text-primary" />
                  Étapes ({etapesTerminees}/{etapes.length})
                </CardTitle>
                <CardDescription>Suivez la progression de votre session</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                {/* Toggle Liste / Timeline */}
                <div className="flex rounded-md border overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setVueTimeline(false)}
                    className={`flex items-center gap-1 px-2.5 py-1.5 text-xs transition-colors ${
                      !vueTimeline ? "bg-primary text-primary-foreground" : "hover:bg-accent"
                    }`}
                    title="Vue liste"
                  >
                    <LayoutList className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline">Liste</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setVueTimeline(true)}
                    className={`flex items-center gap-1 px-2.5 py-1.5 text-xs transition-colors border-l ${
                      vueTimeline ? "bg-primary text-primary-foreground" : "hover:bg-accent"
                    }`}
                    title="Vue timeline"
                  >
                    <BarChart3 className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline">Timeline</span>
                  </button>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={genererAvecRobots}
                  disabled={genererEtapesMutation.isPending || robotsSel.length === 0}
                  title={robotsSel.length === 0 ? "Sélectionnez au moins un appareil" : undefined}
                >
                  {genererEtapesMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Sparkles className="h-4 w-4" />
                  )}
                  <span className="ml-1.5 hidden sm:inline">Régénérer</span>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {vueTimeline ? (
              <TimelineSwimlane etapes={etapes} robotsUtilises={session.robots_utilises} />
            ) : (
              <div className="space-y-2">
                {etapes.map((etape) => {
                  const developpe = etapesExpandees.has(etape.id);
                  const aDescription = Boolean(etape.description);
                  return (
                    <div
                      key={etape.id}
                      className={`rounded-lg border transition-opacity ${
                        etape.est_terminee ? "opacity-60" : ""
                      }`}
                    >
                      {/* Ligne principale */}
                      <div className="flex items-start gap-3 p-3">
                        {etape.est_terminee ? (
                          <CheckCircle2 className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                        ) : (
                          <Circle className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-xs text-muted-foreground font-medium">
                              #{etape.ordre}
                            </span>
                            <p className={`text-sm font-medium ${etape.est_terminee ? "line-through" : ""}`}>
                              {etape.titre}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            {etape.duree_minutes != null && (
                              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Clock className="h-3 w-3" />
                                {etape.duree_minutes} min
                              </span>
                            )}
                            {etape.robots_requis.map((r) => (
                              <Badge key={r} variant="outline" className="text-xs">
                                {r}
                              </Badge>
                            ))}
                            {etape.est_supervision && (
                              <Badge variant="secondary" className="text-xs gap-1">
                                <Timer className="h-3 w-3" />
                                Passif
                              </Badge>
                            )}
                            {etape.groupe_parallele != null && (
                              <Badge variant="secondary" className="text-xs">
                                ∥ Groupe {etape.groupe_parallele}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <Badge
                            className={`text-xs ${
                              etape.est_terminee
                                ? "bg-green-500 hover:bg-green-600"
                                : etape.statut === "en_cours"
                                ? "bg-orange-500 hover:bg-orange-600"
                                : ""
                            }`}
                            variant={
                              etape.est_terminee || etape.statut === "en_cours" ? "default" : "outline"
                            }
                          >
                            {etape.est_terminee
                              ? "✓ Terminée"
                              : etape.statut === "en_cours"
                              ? "En cours"
                              : "En attente"}
                          </Badge>
                          {aDescription && (
                            <button
                              type="button"
                              aria-label={developpe ? "Réduire" : "Développer"}
                              onClick={() => toggleEtape(etape.id)}
                              className="ml-1 rounded p-0.5 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                            >
                              {developpe ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Zone accordéon */}
                      {aDescription && developpe && (
                        <div className="border-t bg-muted/30 px-4 pb-3 pt-2">
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {etape.description}
                          </p>
                          {(etape.temperature != null || etape.est_supervision) && (
                            <div className="flex items-center gap-3 mt-2">
                              {etape.temperature != null && (
                                <span className="flex items-center gap-1 text-xs font-medium text-orange-600 dark:text-orange-400">
                                  <Thermometer className="h-3.5 w-3.5" />
                                  {etape.temperature}°C
                                </span>
                              )}
                              {etape.est_supervision && (
                                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                                  <Timer className="h-3.5 w-3.5" />
                                  L&apos;appareil travaille seul
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Pas d'étapes */}
      {etapes.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-10">
            <ChefHat className="h-10 w-10 text-muted-foreground" />
            <p className="text-muted-foreground text-sm">
              Aucune étape générée pour cette session.
            </p>
            <Button
              onClick={genererAvecRobots}
              disabled={genererEtapesMutation.isPending || robotsSel.length === 0}
            >
              {genererEtapesMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Génération en cours…
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  {robotsSel.length === 0
                    ? "Sélectionnez un appareil ci-dessus"
                    : "Générer les étapes avec l'IA"}
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Dialogue sélection des recettes */}
      <Dialog open={dialogueRecettes} onOpenChange={setDialogueRecettes}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              Recettes de la session
              {recettesSel.length > 0 && (
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  {recettesSel.length} sélectionnée{recettesSel.length > 1 ? "s" : ""}
                </span>
              )}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-3">
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

            <div className="max-h-64 overflow-y-auto space-y-1 rounded-md border p-2">
              {chargementRecettes ? (
                <div className="flex justify-center py-6">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : recettesFiltrees.length === 0 ? (
                <p className="py-4 text-center text-sm text-muted-foreground">Aucune recette trouvée</p>
              ) : (
                recettesFiltrees.map((r) => {
                  const selectionne = recettesSel.includes(r.id);
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
                          <span className="text-xs text-muted-foreground">
                            {r.temps_preparation + (r.temps_cuisson ?? 0)} min
                          </span>
                        )}
                        {selectionne && <CheckCircle2 className="h-4 w-4 text-primary" />}
                      </div>
                    </button>
                  );
                })
              )}
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setDialogueRecettes(false)}>
                Annuler
              </Button>
              <Button
                type="button"
                disabled={enSauvegarde}
                onClick={() => sauvegarderRecettes(undefined)}
              >
                {enSauvegarde && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Enregistrer
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
