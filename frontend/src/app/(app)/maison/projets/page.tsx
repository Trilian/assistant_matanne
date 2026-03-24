// ═══════════════════════════════════════════════════════════
// Projets Maison — Travaux et améliorations
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Hammer, Filter, Clock, CheckCircle2, AlertCircle, Plus, Trash2 } from "lucide-react";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { listerProjets, creerProjet, supprimerProjet } from "@/bibliotheque/api/maison";
import { toast } from "sonner";

const STATUTS = [
  { value: "tous", label: "Tous" },
  { value: "en_cours", label: "En cours" },
  { value: "a_faire", label: "À faire" },
  { value: "termine", label: "Terminé" },
];

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

export default function PageProjets() {
  const [statut, setStatut] = useState("tous");
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [nomProjet, setNomProjet] = useState("");
  const [descProjet, setDescProjet] = useState("");
  const [prioriteProjet, setPrioriteProjet] = useState("moyenne");
  const queryClient = useQueryClient();

  const { data: projets, isLoading } = utiliserRequete(
    ["maison", "projets", statut],
    () => listerProjets(statut === "tous" ? undefined : statut)
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(creerProjet, {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["maison", "projets"] });
      setDialogOuvert(false);
      setNomProjet("");
      setDescProjet("");
      setPrioriteProjet("moyenne");
      toast.success("Projet créé");
    },
    onError: () => toast.error("Erreur lors de la création"),
  });

  const { mutate: supprimer } = utiliserMutation(supprimerProjet, {
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["maison", "projets"] }); toast.success("Projet supprimé"); },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🔨 Projets</h1>
          <p className="text-muted-foreground">
            Travaux et améliorations de la maison
          </p>
        </div>
        <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
          <DialogTrigger asChild>
            <Button><Plus className="mr-2 h-4 w-4" />Nouveau projet</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nouveau projet</DialogTitle>
            </DialogHeader>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                creer({ nom: nomProjet, description: descProjet || undefined, priorite: prioriteProjet, statut: 'planifié' });
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <Label htmlFor="nom">Nom du projet</Label>
                <Input id="nom" value={nomProjet} onChange={(e) => setNomProjet(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="desc">Description</Label>
                <Input id="desc" value={descProjet} onChange={(e) => setDescProjet(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Priorité</Label>
                <Select value={prioriteProjet} onValueChange={setPrioriteProjet}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="haute">Haute</SelectItem>
                    <SelectItem value="moyenne">Moyenne</SelectItem>
                    <SelectItem value="basse">Basse</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" className="w-full" disabled={enCreation || !nomProjet.trim()}>
                {enCreation ? "Création..." : "Créer le projet"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtre statut */}
      <div className="flex items-center gap-3">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <Select value={statut} onValueChange={setStatut}>
          <SelectTrigger className="w-44">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUTS.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Liste projets */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))}
        </div>
      ) : !projets?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Hammer className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucun projet trouvé
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {projets.map((projet) => (
            <Card key={projet.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{projet.nom}</CardTitle>
                  <div className="flex items-center gap-2">
                    {projet.priorite && (
                      <Badge variant={COULEURS_PRIORITE[projet.priorite] ?? "secondary"}>
                        {projet.priorite}
                      </Badge>
                    )}
                    <Badge
                      variant="outline"
                      className={COULEURS_STATUT[projet.statut] ?? ""}
                    >
                      {projet.statut === "en_cours" && (
                        <Clock className="mr-1 h-3 w-3" />
                      )}
                      {projet.statut === "termine" && (
                        <CheckCircle2 className="mr-1 h-3 w-3" />
                      )}
                      {projet.statut === "a_faire" && (
                        <AlertCircle className="mr-1 h-3 w-3" />
                      )}
                      {projet.statut}
                    </Badge>
                  </div>
                </div>
                {projet.description && (
                  <CardDescription>{projet.description}</CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                  {projet.date_debut && (
                    <span>
                      Début:{" "}
                      {new Date(projet.date_debut).toLocaleDateString("fr-FR")}
                    </span>
                  )}
                  {projet.date_fin_prevue && (
                    <span>
                      Fin prévue:{" "}
                      {new Date(projet.date_fin_prevue).toLocaleDateString("fr-FR")}
                    </span>
                  )}
                  <span>{projet.taches_count} tâche(s)</span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-muted-foreground hover:text-destructive"
                  onClick={() => supprimer(projet.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
