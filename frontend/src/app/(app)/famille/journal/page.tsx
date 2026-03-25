// ═══════════════════════════════════════════════════════════
// Journal — Journal familial (connecté API)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  BookOpen,
  Plus,
  Calendar,
  Smile,
  Meh,
  Frown,
  Trash2,
  Sparkles,
  Loader2,
  FileText,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { Input } from "@/composants/ui/input";
import { Textarea } from "@/composants/ui/textarea";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerJournal,
  creerEntreeJournal,
  supprimerEntreeJournal,
  type EntreeJournal,
} from "@/bibliotheque/api/utilitaires";
import {
  obtenirResumeSemaine,
  obtenirRetrospective,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";

const HUMEURS = [
  { value: "bien" as const, label: "Bien", icone: Smile, couleur: "text-green-500" },
  { value: "neutre" as const, label: "Neutre", icone: Meh, couleur: "text-yellow-500" },
  { value: "difficile" as const, label: "Difficile", icone: Frown, couleur: "text-red-500" },
];

export default function PageJournal() {
  const [ouvert, setOuvert] = useState(false);
  const [humeur, setHumeur] = useState("bien");
  const [resumeIA, setResumeIA] = useState("");
  const [retrospectiveIA, setRetrospectiveIA] = useState("");
  const [enChargementResume, setEnChargementResume] = useState(false);
  const [enChargementRetro, setEnChargementRetro] = useState(false);

  const today = new Date();
  const jourSemaine = today.getDay(); // 0 = dimanche, 1 = lundi
  const derniersJourDuMois = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
  const isWeekSummaryDay = jourSemaine === 0 || jourSemaine === 1; // dimanche ou lundi
  const isLastDaysOfMonth = today.getDate() >= derniersJourDuMois - 1; // avant-dernier ou dernier jour du mois

  const genererResume = async () => {
    setEnChargementResume(true);
    try {
      const resultat = await obtenirResumeSemaine({});
      setResumeIA(resultat.resume);
      toast.success("Résumé généré !");
    } catch {
      toast.error("Erreur lors de la génération du résumé");
    } finally {
      setEnChargementResume(false);
    }
  };

  const genererRetrospective = async () => {
    setEnChargementRetro(true);
    try {
      const resultat = await obtenirRetrospective({});
      setRetrospectiveIA(resultat.retrospective);
      toast.success("Rétrospective générée !");
    } catch {
      toast.error("Erreur lors de la génération de la rétrospective");
    } finally {
      setEnChargementRetro(false);
    }
  };

  const sauvegarderResume = () => {
    if (!resumeIA) return;
    // Créer une entrée journal avec le résumé IA
    mutCreer.mutate({
      date_entree: today.toISOString().split("T")[0],
      contenu: `[Résumé IA]\n\n${resumeIA}`,
      humeur: "bien",
      gratitudes: [],
      tags: ["resume-ia"],
    });
    setResumeIA("");
  };

  const invalider = utiliserInvalidation();
  const { data: entrees = [], isLoading } = utiliserRequete(
    ["journal"],
    () => listerJournal()
  );

  const mutCreer = utiliserMutation(
    (e: Omit<EntreeJournal, "id" | "cree_le">) => creerEntreeJournal(e),
    {
      onSuccess: () => { invalider(["journal"]); setOuvert(false); toast.success("Entrée ajoutée"); },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );
  const mutSupprimer = utiliserMutation(
    (id: number) => supprimerEntreeJournal(id),
    {
      onSuccess: () => { invalider(["journal"]); toast.success("Entrée supprimée"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    mutCreer.mutate({
      date_entree: new Date().toISOString().split("T")[0],
      contenu: fd.get("contenu") as string,
      humeur,
      gratitudes: [],
      tags: [],
    });
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            📝 Journal familial
          </h1>
          <p className="text-muted-foreground">
            Souvenirs et moments du quotidien
          </p>
        </div>
        <Dialog open={ouvert} onOpenChange={setOuvert}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle entrée
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Ajouter une entrée</DialogTitle>
            </DialogHeader>
            <form onSubmit={onSubmit} className="space-y-4 pt-2">
              <Textarea
                name="contenu"
                placeholder="Racontez votre journée..."
                required
                rows={4}
              />
              <div>
                <p className="text-sm font-medium mb-2">Humeur du jour</p>
                <div className="flex gap-3">
                  {HUMEURS.map((h) => {
                    const Icone = h.icone;
                    return (
                      <button
                        key={h.value}
                        type="button"
                        onClick={() => setHumeur(h.value)}
                        className={`flex flex-col items-center gap-1 rounded-lg border p-3 transition-colors ${
                          humeur === h.value
                            ? "border-primary bg-primary/10"
                            : "border-transparent hover:bg-accent"
                        }`}
                      >
                        <Icone className={`h-6 w-6 ${h.couleur}`} />
                        <span className="text-xs">{h.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={mutCreer.isPending}>
                Enregistrer
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Section Résumé IA (dimanche/lundi, Phase R1) */}
      {isWeekSummaryDay && (
        <Card className="bg-gradient-to-br from-purple-50/50 to-pink-50/50 dark:from-purple-950/20 dark:to-pink-950/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              <CardTitle className="text-base">Résumé de la semaine</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              L'IA génère un résumé de votre semaine familiale à partir de vos entrées.
            </p>
            <Button
              onClick={genererResume}
              disabled={enChargementResume}
              size="sm"
              className="w-full"
            >
              {enChargementResume ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Génération...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Générer le résumé
                </>
              )}
            </Button>
            {resumeIA && (
              <div className="space-y-2">
                <div className="prose prose-sm dark:prose-invert max-w-none p-3 rounded-lg bg-card border whitespace-pre-wrap">
                  {resumeIA}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={sauvegarderResume}>
                    <FileText className="mr-2 h-3 w-3" />
                    Sauvegarder comme entrée
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setResumeIA("")}
                  >
                    Fermer
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Section Rétrospective IA (dernier jour du mois, Phase R1) */}
      {isLastDaysOfMonth && (
        <Card className="bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-950/20 dark:to-cyan-950/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-500" />
              <CardTitle className="text-base">Rétrospective du mois</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Fin du mois — l'IA crée une rétrospective de vos activités, routines et moments partagés.
            </p>
            <Button
              onClick={genererRetrospective}
              disabled={enChargementRetro}
              size="sm"
              className="w-full"
            >
              {enChargementRetro ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Génération...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Générer la rétrospective
                </>
              )}
            </Button>
            {retrospectiveIA && (
              <div className="space-y-2">
                <div className="prose prose-sm dark:prose-invert max-w-none p-3 rounded-lg bg-card border whitespace-pre-wrap">
                  {retrospectiveIA}
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setRetrospectiveIA("")}
                >
                  Fermer
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Timeline */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <div className="h-5 w-40 animate-pulse rounded bg-muted" />
              </CardHeader>
              <CardContent>
                <div className="h-4 w-full animate-pulse rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : entrees.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-10 text-muted-foreground">
            <BookOpen className="h-8 w-8 opacity-50" />
            Commencez à écrire votre journal familial
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {entrees.map((entree) => {
            const humeurInfo = HUMEURS.find((h) => h.value === entree.humeur);
            const HumeurIcone = humeurInfo?.icone ?? Smile;
            return (
              <Card key={entree.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">
                      {entree.date_entree}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <HumeurIcone
                        className={`h-4 w-4 ${humeurInfo?.couleur ?? ""}`}
                      />
                      <Badge variant="secondary" className="text-xs">
                        <Calendar className="mr-1 h-3 w-3" />
                        {new Date(entree.date_entree).toLocaleDateString(
                          "fr-FR",
                          { day: "numeric", month: "short" }
                        )}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 text-destructive"
                        onClick={() => mutSupprimer.mutate(entree.id)}
                        aria-label="Supprimer l'entrée"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground whitespace-pre-line">
                    {entree.contenu}
                  </p>
                  {entree.tags.length > 0 && (
                    <div className="mt-2 flex gap-1">
                      {entree.tags.map((t) => (
                        <Badge key={t} variant="outline" className="text-xs">
                          {t}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
