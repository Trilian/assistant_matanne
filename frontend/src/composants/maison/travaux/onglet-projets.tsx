"use client";

import { useState } from "react";
import { BotMessageSquare, Hammer, Plus, Trash2, Wifi, WifiOff } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import { EtatVide } from "@/composants/ui/etat-vide";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/composants/ui/select";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import { utiliserAutoCompletionMaison } from "@/crochets/utiliser-auto-completion-maison";
import { utiliserWebSocket } from "@/crochets/utiliser-websocket";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { KanbanProjets } from "@/composants/maison/kanban-projets";
import { creerProjet, listerProjets, modifierProjet, supprimerProjet } from "@/bibliotheque/api/maison";
import { GanttProjets } from "@/composants/maison/travaux/gantt-projets";
import { toast } from "sonner";

import { SheetEstimationIA } from "./sheet-estimation-ia";

const COULEURS_STATUT: Record<string, string> = {
  en_cours: "bg-blue-500/10 text-blue-600",
  a_faire: "bg-yellow-500/10 text-yellow-600",
  termine: "bg-green-500/10 text-green-600",
  annule: "bg-red-500/10 text-red-600",
};

const COULEURS_PRIORITE: Record<string, "default" | "secondary" | "destructive"> = {
  haute: "destructive",
  moyenne: "default",
  basse: "secondary",
};

export function OngletProjets() {
  const [statut, setStatut] = useState("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [etapeCreation, setEtapeCreation] = useState(1);
  const [nomProjet, setNomProjet] = useState("");
  const [descProjet, setDescProjet] = useState("");
  const [prioriteProjet, setPrioriteProjet] = useState("moyenne");
  const [categorieProjet, setCategorieProjet] = useState("");
  const [budgetProjet, setBudgetProjet] = useState("");
  const [tachesSelectionnees, setTachesSelectionnees] = useState<string[]>([]);
  const [estimationProjetId, setEstimationProjetId] = useState<number | null>(null);
  const queryClient = useQueryClient();
  const { utilisateur } = utiliserAuth();
  const identifiantPresence = String(utilisateur?.id ?? utilisateur?.email ?? "maison-projets");
  const nomPresence = String(utilisateur?.nom ?? "Maison");
  const baseWs = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/^http/, "ws");
  const {
    connecte: synchroActive,
    utilisateurs: collaborateurs,
    envoyer: diffuserProjet,
    mode: modeSynchro,
  } = utiliserWebSocket({
    url: `${baseWs}/api/v1/ws/projets/1?user=${encodeURIComponent(identifiantPresence)}&username=${encodeURIComponent(nomPresence)}`,
    gestionnaires: {
      tache_added: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresence) {
          queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
        }
      },
      tache_moved: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresence) {
          queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
        }
      },
      tache_removed: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresence) {
          queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
        }
      },
    },
    maxTentatives: 3,
  });
  const { autoCompleter } = utiliserAutoCompletionMaison("travaux_projets");

  const suggestionsTaches = [
    "Definir le besoin et les contraintes",
    "Comparer 2 devis minimum",
    "Commander les materiaux",
    "Planifier les etapes",
  ];

  const reinitialiserWizard = () => {
    setEtapeCreation(1);
    setNomProjet("");
    setDescProjet("");
    setPrioriteProjet("moyenne");
    setCategorieProjet("");
    setBudgetProjet("");
    setTachesSelectionnees([]);
  };

  const { data: projets, isLoading } = utiliserRequete(
    ["maison", "projets", statut],
    () => listerProjets(statut === "tous" ? undefined : statut)
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(creerProjet, {
    onSuccess: (nouveauProjet) => {
      queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
      diffuserProjet({ action: "tache_added", data: { projet_id: nouveauProjet.id, statut: nouveauProjet.statut } });
      setDialogOuvert(false);
      reinitialiserWizard();
      toast.success("Projet créé");
      toast("💡 Estimer ce projet avec l'IA ?", {
        action: {
          label: "Estimer",
          onClick: () => setEstimationProjetId(nouveauProjet.id),
        },
      });
    },
    onError: () => toast.error("Erreur lors de la création"),
  });

  const { mutate: supprimer } = utiliserMutation(supprimerProjet, {
    onSuccess: (_resultat, projetId) => {
      queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
      diffuserProjet({ action: "tache_removed", data: { projet_id: projetId } });
      toast.success("Projet supprimé");
    },
  });

  const { mutate: deplacerProjet, isPending: deplacementStatutEnCours } = utiliserMutation(
    ({ id, statut }: { id: number; statut: string }) => modifierProjet(id, { statut }),
    {
      onSuccess: (_resultat, variables) => {
        queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
        diffuserProjet({ action: "tache_moved", data: { projet_id: variables.id, statut: variables.statut } });
      },
      onError: () => toast.error("Impossible de déplacer le projet"),
    }
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={synchroActive ? "default" : modeSynchro === "polling" ? "secondary" : "outline"}>
            {synchroActive ? (
              <span className="inline-flex items-center gap-1"><Wifi className="h-3 w-3" /> Live</span>
            ) : (
              <span className="inline-flex items-center gap-1"><WifiOff className="h-3 w-3" /> {modeSynchro === "polling" ? "Fallback" : "Hors ligne"}</span>
            )}
          </Badge>
          <Badge variant="outline">{collaborateurs.length} connecté(s)</Badge>
        </div>
        <Select value={statut} onValueChange={setStatut}>
          <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="tous">Tous</SelectItem>
            <SelectItem value="en_cours">En cours</SelectItem>
            <SelectItem value="a_faire">À faire</SelectItem>
            <SelectItem value="termine">Terminé</SelectItem>
          </SelectContent>
        </Select>

        <Dialog
          open={dialogOuvert}
          onOpenChange={(ouvert) => {
            setDialogOuvert(ouvert);
            if (!ouvert) reinitialiserWizard();
          }}
        >
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="mr-2 h-4 w-4" />Nouveau projet</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Wizard projet maison (3 etapes)</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (etapeCreation < 3) {
                  setEtapeCreation((v) => v + 1);
                  return;
                }
                const segments = [descProjet.trim()];
                if (categorieProjet.trim()) segments.push(`Type: ${categorieProjet.trim()}`);
                if (budgetProjet.trim()) segments.push(`Budget cible: ${budgetProjet.trim()} EUR`);
                if (tachesSelectionnees.length > 0) {
                  segments.push(`Taches suggerees: ${tachesSelectionnees.join(", ")}`);
                }

                creer({
                  nom: nomProjet,
                  description: segments.filter(Boolean).join(" | ") || undefined,
                  priorite: prioriteProjet,
                  statut: "planifié",
                });
              }}
              className="space-y-4"
            >
              <div className="text-xs text-muted-foreground">Etape {etapeCreation} / 3</div>

              {etapeCreation === 1 && (
                <div className="space-y-2">
                  <Label>Nom du projet</Label>
                  <Input
                    value={nomProjet}
                    onChange={(e) => setNomProjet(e.target.value)}
                    onBlur={(e) => autoCompleter("nom_projet", e.target.value, (v) => { if (!categorieProjet) setCategorieProjet(v); })}
                    required
                    placeholder="Ex: Refaire la salle de bain"
                  />
                  <Label>Description rapide</Label>
                  <Input
                    value={descProjet}
                    onChange={(e) => setDescProjet(e.target.value)}
                    placeholder="Contexte du projet"
                  />
                </div>
              )}

              {etapeCreation === 2 && (
                <div className="space-y-3">
                  <div className="space-y-2">
                    <Label>Type de projet</Label>
                    <Input
                      value={categorieProjet}
                      onChange={(e) => setCategorieProjet(e.target.value)}
                      placeholder="Renovation, energie, menage..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Budget cible (EUR)</Label>
                    <Input
                      type="number"
                      min="0"
                      value={budgetProjet}
                      onChange={(e) => setBudgetProjet(e.target.value)}
                      placeholder="1500"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Priorite</Label>
                    <Select value={prioriteProjet} onValueChange={setPrioriteProjet}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="haute">Haute</SelectItem>
                        <SelectItem value="moyenne">Moyenne</SelectItem>
                        <SelectItem value="basse">Basse</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              {etapeCreation === 3 && (
                <div className="space-y-2">
                  <Label>Taches suggerees (IA)</Label>
                  <div className="space-y-2">
                    {suggestionsTaches.map((tache) => {
                      const actif = tachesSelectionnees.includes(tache);
                      return (
                        <button
                          key={tache}
                          type="button"
                          className={`w-full rounded-md border px-3 py-2 text-left text-sm ${actif ? "border-primary bg-primary/10" : ""}`}
                          onClick={() => {
                            setTachesSelectionnees((prev) =>
                              prev.includes(tache)
                                ? prev.filter((x) => x !== tache)
                                : [...prev, tache]
                            );
                          }}
                        >
                          {tache}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  disabled={etapeCreation === 1 || enCreation}
                  onClick={() => setEtapeCreation((v) => Math.max(1, v - 1))}
                >
                  Retour
                </Button>
                <Button type="submit" disabled={enCreation || !nomProjet.trim()} className="w-full">
                  {enCreation ? "Creation..." : etapeCreation < 3 ? "Continuer" : "Creer le projet"}
                </Button>
              </div>

              <Button
                type="button"
                variant="ghost"
                className="w-full"
                onClick={() => {
                  setDialogOuvert(false);
                  reinitialiserWizard();
                }}
              >
                Annuler
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {!isLoading && !!projets?.length ? <GanttProjets projets={projets} /> : null}

      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-32" />)}</div>
      ) : !projets?.length ? (
        <Card>
          <CardContent className="py-6">
            <EtatVide
              Icone={Hammer}
              titre={`Aucun projet${statut !== "tous" ? " dans ce statut" : ""}`}
              description="Ajoutez un projet ou changez le filtre pour voir plus d'elements."
            />
          </CardContent>
        </Card>
      ) : statut === "tous" ? (
        <KanbanProjets
          projets={projets}
          onSupprimer={(id) => supprimer(id)}
          onEstimer={(id) => setEstimationProjetId(id)}
          onDeplacerStatut={(projetId, statutCible) => {
            deplacerProjet({ id: projetId, statut: statutCible });
          }}
          enCours={deplacementStatutEnCours}
        />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {projets.map((projet) => (
            <Card key={projet.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm">{projet.nom}</CardTitle>
                  <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0 text-muted-foreground hover:text-destructive" onClick={() => supprimer(projet.id)}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${COULEURS_STATUT[projet.statut] ?? ""}`}>
                    {projet.statut.replace("_", " ")}
                  </span>
                  {projet.priorite && (
                    <Badge variant={COULEURS_PRIORITE[projet.priorite] ?? "outline"} className="text-xs">
                      {projet.priorite}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              {projet.description && (
                <CardContent className="pb-2 pt-0">
                  <p className="line-clamp-2 text-xs text-muted-foreground">{projet.description}</p>
                </CardContent>
              )}
              <CardContent className="pb-3 pt-0">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 w-full gap-1 text-xs"
                  onClick={() => setEstimationProjetId(projet.id)}
                >
                  <BotMessageSquare className="h-3.5 w-3.5" />
                  Estimer avec l&apos;IA
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <SheetEstimationIA
        projetId={estimationProjetId}
        ouvert={estimationProjetId !== null}
        onFermer={() => setEstimationProjetId(null)}
      />
    </div>
  );
}
