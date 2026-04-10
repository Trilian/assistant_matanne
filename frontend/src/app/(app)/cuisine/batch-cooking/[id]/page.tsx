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

export default function PageDetailBatch() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const { definirTitrePage } = utiliserStoreUI();
  const invalider = utiliserInvalidation();

  const [dialogueRecettes, setDialogueRecettes] = useState(false);
  const [recettesSel, setRecettesSel] = useState<number[]>([]);
  const [rechercheRecette, setRechercheRecette] = useState("");

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
        invalider(["batch-cooking", String(id)]);
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

  useEffect(() => {
    if (session?.nom) definirTitrePage(session.nom);
    return () => definirTitrePage(null);
  }, [session?.nom, definirTitrePage]);

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

      {/* Robots utilisés */}
      {session.robots_utilises.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Bot className="h-4 w-4" />
              Robots utilisés
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {session.robots_utilises.map((r) => (
                <Badge key={r} variant="secondary">
                  {r}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Étapes */}
      {etapes.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <div>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Loader2 className="h-5 w-5 text-primary" />
                  Étapes ({etapesTerminees}/{etapes.length})
                </CardTitle>
                <CardDescription>
                  Suivez la progression de votre session
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => genererEtapesMutation.mutate()}
                disabled={genererEtapesMutation.isPending}
              >
                {genererEtapesMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                <span className="ml-1.5 hidden sm:inline">Régénérer</span>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {etapes.map((etape) => (
                <div
                  key={etape.id}
                  className={`flex items-start gap-3 rounded-lg border p-3 transition-opacity ${
                    etape.est_terminee ? "opacity-60" : ""
                  }`}
                >
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
                      {etape.duree_minutes && (
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
                      {etape.groupe_parallele !== undefined && etape.groupe_parallele !== null && (
                        <Badge variant="secondary" className="text-xs">
                          ∥ Groupe {etape.groupe_parallele}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Badge
                    className={`text-xs shrink-0 ${
                      etape.est_terminee
                        ? "bg-green-500 hover:bg-green-600"
                        : etape.statut === "en_cours"
                        ? "bg-orange-500 hover:bg-orange-600"
                        : ""
                    }`}
                    variant={etape.est_terminee || etape.statut === "en_cours" ? "default" : "outline"}
                  >
                    {etape.est_terminee
                      ? "✓ Terminée"
                      : etape.statut === "en_cours"
                      ? "En cours"
                      : "En attente"}
                  </Badge>
                </div>
              ))}
            </div>
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
              onClick={() => genererEtapesMutation.mutate()}
              disabled={genererEtapesMutation.isPending}
            >
              {genererEtapesMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Génération en cours…
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Générer les étapes avec l'IA
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
