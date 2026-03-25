// ═══════════════════════════════════════════════════════════
// Activités familiales
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Plus,
  CalendarHeart,
  MapPin,
  Clock,
  Users,
  Loader2,
  Check,
  Filter,
} from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import { listerActivites, creerActivite } from "@/bibliotheque/api/famille";
import type { Activite } from "@/types/famille";
import { toast } from "sonner";

const TYPES_ACTIVITE = [
  "tous",
  "sortie",
  "jeu",
  "sport",
  "culture",
  "repas",
  "visite",
  "autre",
];

export default function PageActivites() {
  const [typeFiltre, setTypeFiltre] = useState("tous");
  const [dialogueCreation, setDialogueCreation] = useState(false);

  // Form state
  const [titre, setTitre] = useState("");
  const [type, setType] = useState("sortie");
  const [date, setDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [lieu, setLieu] = useState("");
  const [duree, setDuree] = useState("");
  const [description, setDescription] = useState("");

  const invalider = utiliserInvalidation();

  const { data: activites, isLoading } = utiliserRequete(
    ["famille", "activites", typeFiltre],
    () => listerActivites(typeFiltre !== "tous" ? typeFiltre : undefined)
  );

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (act: Omit<Activite, "id">) => creerActivite(act),
    {
      onSuccess: () => {
        invalider(["famille", "activites"]);
        setDialogueCreation(false);
        setTitre("");
        setLieu("");
        setDuree("");
        setDescription("");
        toast.success("Activité créée");
      },
      onError: () => toast.error("Erreur lors de la création"),
    }
  );

  const activitesAVenir = (activites ?? []).filter((a) => !a.est_terminee);
  const activitesPassees = (activites ?? []).filter((a) => a.est_terminee);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            🎉 Activités
          </h1>
          <p className="text-muted-foreground">
            Activités familiales et sorties
          </p>
        </div>
        <Button onClick={() => setDialogueCreation(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Nouvelle activité
        </Button>
      </div>

      {/* Filtre type */}
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <Select value={typeFiltre} onValueChange={setTypeFiltre}>
          <SelectTrigger className="w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {TYPES_ACTIVITE.map((t) => (
              <SelectItem key={t} value={t}>
                {t === "tous" ? "Tous les types" : t.charAt(0).toUpperCase() + t.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      ) : !activites?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-12">
            <CalendarHeart className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aucune activité planifiée</p>
            <Button
              variant="outline"
              onClick={() => setDialogueCreation(true)}
            >
              <Plus className="mr-1 h-4 w-4" />
              Planifier une activité
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* À venir */}
          {activitesAVenir.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">À venir</h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {activitesAVenir.map((a) => (
                  <ActiviteCard key={a.id} activite={a} />
                ))}
              </div>
            </div>
          )}

          {/* Passées */}
          {activitesPassees.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-semibold text-muted-foreground">
                Terminées
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 opacity-70">
                {activitesPassees.map((a) => (
                  <ActiviteCard key={a.id} activite={a} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Dialogue création */}
      <Dialog open={dialogueCreation} onOpenChange={setDialogueCreation}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nouvelle activité</DialogTitle>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              if (!titre.trim()) return;
              creer({
                titre: titre.trim(),
                type,
                date,
                description: description || undefined,
                lieu: lieu || undefined,
                duree_minutes: duree ? Number(duree) : undefined,
                est_terminee: false,
              });
            }}
          >
            <div className="space-y-2">
              <Label htmlFor="act-titre">Titre *</Label>
              <Input
                id="act-titre"
                value={titre}
                onChange={(e) => setTitre(e.target.value)}
                placeholder="Ex: Sortie au parc"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Type</Label>
                <Select value={type} onValueChange={setType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TYPES_ACTIVITE.filter((t) => t !== "tous").map((t) => (
                      <SelectItem key={t} value={t}>
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="act-date">Date *</Label>
                <Input
                  id="act-date"
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="act-lieu">Lieu</Label>
                <Input
                  id="act-lieu"
                  value={lieu}
                  onChange={(e) => setLieu(e.target.value)}
                  placeholder="Lieu..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="act-duree">Durée (min)</Label>
                <Input
                  id="act-duree"
                  type="number"
                  min={0}
                  value={duree}
                  onChange={(e) => setDuree(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="act-desc">Description</Label>
              <Input
                id="act-desc"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Détails..."
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => setDialogueCreation(false)}
              >
                Annuler
              </Button>
              <Button type="submit" disabled={enCreation || !titre.trim()}>
                {enCreation && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Créer
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function ActiviteCard({ activite: a }: { activite: Activite }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{a.titre}</CardTitle>
          <div className="flex gap-1">
            <Badge variant="outline" className="text-xs capitalize">
              {a.type}
            </Badge>
            {a.est_terminee && (
              <Badge variant="secondary" className="text-xs">
                <Check className="mr-1 h-3 w-3" />
                Fait
              </Badge>
            )}
          </div>
        </div>
        {a.description && (
          <CardDescription>{a.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="flex flex-wrap gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <CalendarHeart className="h-3 w-3" />
          {new Date(a.date).toLocaleDateString("fr-FR", {
            weekday: "short",
            day: "numeric",
            month: "short",
          })}
        </span>
        {a.lieu && (
          <span className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {a.lieu}
          </span>
        )}
        {a.duree_minutes && (
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {a.duree_minutes} min
          </span>
        )}
        {a.participants && a.participants.length > 0 && (
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {a.participants.length}
          </span>
        )}
      </CardContent>
    </Card>
  );
}
