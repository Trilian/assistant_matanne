"use client";

import { useState } from "react";
import { Activity, AlertTriangle, CheckCircle2, Plus, SprayCan, Trash2 } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/composants/ui/dialog";
import { EtatVide } from "@/composants/ui/etat-vide";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import { Badge } from "@/composants/ui/badge";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  creerTacheEntretien,
  listerTachesEntretien,
  obtenirSanteAppareils,
  supprimerTacheEntretien,
} from "@/bibliotheque/api/maison";
import { toast } from "sonner";

export function OngletEntretien() {
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [nom, setNom] = useState("");
  const [categorie, setCategorie] = useState("");
  const [piece, setPiece] = useState("");
  const [frequence, setFrequence] = useState("");
  const queryClient = useQueryClient();

  const { data: taches, isLoading: chargementTaches } = utiliserRequete(
    ["maison", "entretien", "taches"],
    () => listerTachesEntretien()
  );
  const { data: sante, isLoading: chargementSante } = utiliserRequete(
    ["maison", "entretien", "sante"],
    obtenirSanteAppareils
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
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
    }
  );

  const { mutate: supprimer } = utiliserMutation((id: number) => supprimerTacheEntretien(id), {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maison", "entretien"] });
      toast.success("Tâche supprimée");
    },
  });

  const tachesEnRetard = taches?.filter((t) => t.prochaine_fois && new Date(t.prochaine_fois) < new Date() && !t.fait) ?? [];
  const tachesNormales = taches?.filter((t) => !tachesEnRetard.includes(t)) ?? [];

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="mr-2 h-4 w-4" />Nouvelle tâche</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nouvelle tâche d&apos;entretien</DialogTitle></DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                creer({
                  nom,
                  categorie: categorie || undefined,
                  piece: piece || undefined,
                  frequence_jours: frequence ? Number(frequence) : undefined,
                });
              }}
              className="space-y-4"
            >
              <div className="space-y-2"><Label>Nom</Label><Input value={nom} onChange={(e) => setNom(e.target.value)} required /></div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2"><Label>Catégorie</Label><Input value={categorie} onChange={(e) => setCategorie(e.target.value)} /></div>
                <div className="space-y-2"><Label>Pièce</Label><Input value={piece} onChange={(e) => setPiece(e.target.value)} /></div>
              </div>
              <div className="space-y-2"><Label>Fréquence (jours)</Label><Input type="number" value={frequence} onChange={(e) => setFrequence(e.target.value)} /></div>
              <Button type="submit" disabled={enCreation} className="w-full">{enCreation ? "Création…" : "Créer"}</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {!chargementSante && sante && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Activity className="h-4 w-4" />
              Santé des appareils
              <Badge
                variant={sante.score_global >= 80 ? "secondary" : sante.score_global >= 50 ? "default" : "destructive"}
                className="ml-auto"
              >
                {sante.score_global}%
              </Badge>
            </CardTitle>
          </CardHeader>
          {sante.actions_urgentes?.length > 0 && (
            <CardContent className="pt-0">
              {sante.actions_urgentes.slice(0, 3).map((action, i) => (
                <p key={i} className="flex items-center gap-1 text-xs text-muted-foreground">
                  <AlertTriangle className="h-3 w-3 shrink-0 text-amber-500" />
                  {action.tache} ({action.zone})
                </p>
              ))}
            </CardContent>
          )}
        </Card>
      )}

      {tachesEnRetard.length > 0 && (
        <div>
          <p className="mb-2 flex items-center gap-1.5 text-sm font-medium text-destructive">
            <AlertTriangle className="h-4 w-4" />
            {tachesEnRetard.length} tâche(s) en retard
          </p>
          <div className="space-y-2">
            {tachesEnRetard.map((tache) => (
              <Card key={tache.id} className="border-destructive/30">
                <CardContent className="flex items-center gap-2 py-3">
                  <AlertTriangle className="h-4 w-4 shrink-0 text-destructive" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{tache.nom}</p>
                    <p className="text-xs text-muted-foreground">{tache.categorie}{tache.piece ? ` · ${tache.piece}` : ""}</p>
                  </div>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => supprimer(tache.id)}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {chargementTaches ? (
        <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14" />)}</div>
      ) : (
        <div className="space-y-2">
          {tachesNormales.map((tache) => (
            <Card key={tache.id}>
              <CardContent className="flex items-center gap-2 py-3">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm">{tache.nom}</p>
                  <p className="text-xs text-muted-foreground">
                    {tache.categorie}
                    {tache.piece ? ` · ${tache.piece}` : ""}
                    {tache.frequence_jours ? ` · tous les ${tache.frequence_jours}j` : ""}
                  </p>
                </div>
                <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => supprimer(tache.id)}>
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </CardContent>
            </Card>
          ))}
          {!tachesNormales.length && !tachesEnRetard.length && (
            <Card>
              <CardContent className="py-6">
                <EtatVide
                  Icone={SprayCan}
                  titre="Aucune tache d'entretien"
                  description="Ajoutez une tache recurrente pour lancer votre routine maison."
                />
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
