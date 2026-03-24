// ═══════════════════════════════════════════════════════════
// Entretien — Tâches ménagères et santé appareils
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { SprayCan, AlertTriangle, CheckCircle2, Activity, Clock, Plus, Trash2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import {
  listerTachesEntretien,
  obtenirSanteAppareils,
  creerTacheEntretien,
  supprimerTacheEntretien,
} from "@/bibliotheque/api/maison";
import { toast } from "sonner";

export default function PageEntretien() {
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [nom, setNom] = useState("");
  const [categorie, setCategorie] = useState("");
  const [piece, setPiece] = useState("");
  const [frequence, setFrequence] = useState("");

  const queryClient = useQueryClient();

  const mutationCreer = utiliserMutation(
    (data: { nom: string; categorie?: string; piece?: string; frequence_jours?: number }) =>
      creerTacheEntretien({ ...data, fait: false }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["maison", "entretien"] });
        setDialogOuvert(false);
        setNom("");
        setCategorie("");
        setPiece("");
        setFrequence("");
        toast.success("Tâche créée");
      },
      onError: () => toast.error("Erreur lors de la création"),
    }
  );

  const mutationSupprimer = utiliserMutation(
    (id: number) => supprimerTacheEntretien(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ["maison", "entretien"] });
        toast.success("Tâche supprimée");
      },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  const { data: taches, isLoading: chargementTaches } = utiliserRequete(
    ["maison", "entretien", "taches"],
    () => listerTachesEntretien()
  );

  const { data: sante, isLoading: chargementSante } = utiliserRequete(
    ["maison", "entretien", "sante"],
    obtenirSanteAppareils
  );

  const tachesEnRetard = taches?.filter(
    (t) => t.prochaine_fois && new Date(t.prochaine_fois) < new Date() && !t.fait
  );
  const tachesAJour = taches?.filter(
    (t) => !tachesEnRetard?.includes(t)
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🧹 Entretien</h1>
        <p className="text-muted-foreground">
          Tâches ménagères et santé des appareils
        </p>
      </div>

      <Tabs defaultValue="taches">
        <TabsList>
          <TabsTrigger value="taches">
            <SprayCan className="mr-2 h-4 w-4" />
            Tâches
          </TabsTrigger>
          <TabsTrigger value="sante">
            <Activity className="mr-2 h-4 w-4" />
            Santé appareils
          </TabsTrigger>
        </TabsList>

        {/* ─── Onglet Tâches ─────────────────────────── */}
        <TabsContent value="taches" className="space-y-4 mt-4">
          <div className="flex justify-end">
            <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-1" /> Ajouter
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Nouvelle tâche d&apos;entretien</DialogTitle>
                </DialogHeader>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (!nom) return;
                    mutationCreer.mutate({
                      nom,
                      categorie: categorie || undefined,
                      piece: piece || undefined,
                      frequence_jours: frequence ? parseInt(frequence) : undefined,
                    });
                  }}
                  className="space-y-4"
                >
                  <div>
                    <Label>Nom</Label>
                    <Input value={nom} onChange={(e) => setNom(e.target.value)} required />
                  </div>
                  <div>
                    <Label>Catégorie</Label>
                    <Input value={categorie} onChange={(e) => setCategorie(e.target.value)} placeholder="ex: ménage, plomberie…" />
                  </div>
                  <div>
                    <Label>Pièce</Label>
                    <Input value={piece} onChange={(e) => setPiece(e.target.value)} placeholder="ex: cuisine, salle de bain…" />
                  </div>
                  <div>
                    <Label>Fréquence (jours)</Label>
                    <Input type="number" value={frequence} onChange={(e) => setFrequence(e.target.value)} placeholder="ex: 30" />
                  </div>
                  <Button type="submit" className="w-full" disabled={mutationCreer.isPending}>
                    {mutationCreer.isPending ? "Ajout…" : "Ajouter la tâche"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {chargementTaches ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-20" />
              ))}
            </div>
          ) : !taches?.length ? (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                <SprayCan className="h-8 w-8 mx-auto mb-2 opacity-50" />
                Aucune tâche d&apos;entretien
              </CardContent>
            </Card>
          ) : (
            <>
              {/* En retard */}
              {tachesEnRetard && tachesEnRetard.length > 0 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-semibold text-destructive flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    En retard ({tachesEnRetard.length})
                  </h2>
                  <div className="space-y-2">
                    {tachesEnRetard.map((t) => (
                      <Card key={t.id} className="border-destructive/30">
                        <CardContent className="flex items-center justify-between py-3">
                          <div>
                            <p className="text-sm font-medium">{t.nom}</p>
                            <div className="flex gap-2 text-xs text-muted-foreground mt-1">
                              {t.piece && <span>{t.piece}</span>}
                              {t.prochaine_fois && (
                                <span className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  Prévu le{" "}
                                  {new Date(t.prochaine_fois).toLocaleDateString("fr-FR")}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="destructive" className="text-xs">
                              En retard
                            </Badge>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 text-destructive"
                              onClick={() => mutationSupprimer.mutate(t.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* À jour */}
              {tachesAJour && tachesAJour.length > 0 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-semibold flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Planifiées ({tachesAJour.length})
                  </h2>
                  <div className="space-y-2">
                    {tachesAJour.map((t) => (
                      <Card key={t.id}>
                        <CardContent className="flex items-center justify-between py-3">
                          <div>
                            <p className="text-sm font-medium">{t.nom}</p>
                            <div className="flex gap-3 text-xs text-muted-foreground mt-1">
                              {t.piece && <span>{t.piece}</span>}
                              {t.categorie && (
                                <Badge variant="outline" className="text-xs">
                                  {t.categorie}
                                </Badge>
                              )}
                              {t.frequence_jours && (
                                <span>Tous les {t.frequence_jours}j</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {t.fait ? (
                              <Badge className="bg-green-500/10 text-green-600 text-xs">
                                Fait
                              </Badge>
                            ) : t.prochaine_fois ? (
                              <span className="text-xs text-muted-foreground">
                                {new Date(t.prochaine_fois).toLocaleDateString("fr-FR")}
                              </span>
                            ) : null}
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 text-destructive"
                              onClick={() => mutationSupprimer.mutate(t.id)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </TabsContent>

        {/* ─── Onglet Santé ──────────────────────────── */}
        <TabsContent value="sante" className="space-y-4 mt-4">
          {chargementSante ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-20" />
              ))}
            </div>
          ) : sante ? (
            <>
              {/* Score global */}
              <Card className="border-primary/30 bg-primary/5">
                <CardContent className="py-4 text-center">
                  <p className="text-3xl font-bold">{sante.score_global}%</p>
                  <p className="text-sm text-muted-foreground">Score de santé global</p>
                </CardContent>
              </Card>

              {/* Zones */}
              <div className="grid gap-3 sm:grid-cols-2">
                {sante.zones.map((zone) => (
                  <Card key={zone.zone}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">{zone.zone}</CardTitle>
                      <CardDescription className="text-xs">
                        {zone.taches_a_jour}/{zone.total_taches} tâches à jour
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              zone.score_sante >= 80
                                ? "bg-green-500"
                                : zone.score_sante >= 50
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                            }`}
                            style={{ width: `${zone.score_sante}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">
                          {zone.score_sante}%
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Actions urgentes */}
              {sante.actions_urgentes.length > 0 && (
                <div className="space-y-2">
                  <h2 className="text-sm font-semibold text-destructive flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" />
                    Actions urgentes
                  </h2>
                  {sante.actions_urgentes.map((a, i) => (
                    <Card key={i} className="border-destructive/20">
                      <CardContent className="flex items-center justify-between py-3">
                        <div>
                          <p className="text-sm font-medium">{a.tache}</p>
                          <p className="text-xs text-muted-foreground">
                            {a.zone}
                          </p>
                        </div>
                        <Badge variant="destructive" className="text-xs">
                          {a.jours_retard}j de retard
                        </Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-10 text-center text-muted-foreground">
                Aucune donnée de santé disponible
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
