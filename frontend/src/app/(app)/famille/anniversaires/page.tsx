// ═══════════════════════════════════════════════════════════
// Anniversaires — Dates importantes (connecté API)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Cake, Gift, Calendar, Plus, Trash2, Pencil } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/composants/ui/dialog";
import {
  utiliserRequete,
  utiliserMutation,
  utiliserInvalidation,
} from "@/crochets/utiliser-api";
import {
  listerAnniversaires,
  creerAnniversaire,
  modifierAnniversaire,
  supprimerAnniversaire,
  type Anniversaire,
} from "@/bibliotheque/api/famille";
import { toast } from "sonner";

const RELATIONS = [
  "enfant",
  "parent",
  "grand_parent",
  "oncle_tante",
  "cousin",
  "ami",
  "collegue",
];
const LABELS_REL: Record<string, string> = {
  enfant: "Enfant",
  parent: "Parent",
  grand_parent: "Grand-parent",
  oncle_tante: "Oncle/Tante",
  cousin: "Cousin(e)",
  ami: "Ami(e)",
  collegue: "Collègue",
};

export default function PageAnniversaires() {
  const [ouvert, setOuvert] = useState(false);
  const [edition, setEdition] = useState<Anniversaire | null>(null);

  const invalider = utiliserInvalidation();
  const { data: anniversaires = [], isLoading } = utiliserRequete(
    ["anniversaires"],
    () => listerAnniversaires()
  );

  const mutCreer = utiliserMutation(
    (a: Parameters<typeof creerAnniversaire>[0]) => creerAnniversaire(a),
    {
      onSuccess: () => { invalider(["anniversaires"]); setOuvert(false); toast.success("Anniversaire ajouté"); },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );
  const mutModifier = utiliserMutation(
    ({ id, patch }: { id: number; patch: Partial<Anniversaire> }) =>
      modifierAnniversaire(id, patch),
    {
      onSuccess: () => { invalider(["anniversaires"]); setEdition(null); setOuvert(false); toast.success("Anniversaire modifié"); },
      onError: () => toast.error("Erreur lors de la modification"),
    }
  );
  const mutSupprimer = utiliserMutation(
    (id: number) => supprimerAnniversaire(id),
    {
      onSuccess: () => { invalider(["anniversaires"]); toast.success("Anniversaire supprimé"); },
      onError: () => toast.error("Erreur lors de la suppression"),
    }
  );

  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload = {
      nom_personne: fd.get("nom_personne") as string,
      date_naissance: fd.get("date_naissance") as string,
      relation: fd.get("relation") as string,
      rappel_jours_avant: [7, 1, 0],
      idees_cadeaux: (fd.get("idees_cadeaux") as string) || undefined,
      notes: (fd.get("notes") as string) || undefined,
    };
    if (edition) {
      mutModifier.mutate({ id: edition.id, patch: payload });
    } else {
      mutCreer.mutate(payload);
    }
  }

  function ouvrir(a?: Anniversaire) {
    setEdition(a ?? null);
    setOuvert(true);
  }

  const prochain = anniversaires[0];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            🎂 Anniversaires
          </h1>
          <p className="text-muted-foreground">
            Dates importantes à ne pas oublier
          </p>
        </div>
        <Dialog open={ouvert} onOpenChange={(o) => { setOuvert(o); if (!o) setEdition(null); }}>
          <DialogTrigger asChild>
            <Button onClick={() => ouvrir()}>
              <Plus className="mr-2 h-4 w-4" />
              Ajouter
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {edition ? "Modifier" : "Nouvel anniversaire"}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={onSubmit} className="space-y-3 pt-2">
              <div>
                <Label htmlFor="nom_personne">Nom *</Label>
                <Input
                  id="nom_personne"
                  name="nom_personne"
                  required
                  defaultValue={edition?.nom_personne ?? ""}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="date_naissance">Date de naissance *</Label>
                  <Input
                    id="date_naissance"
                    name="date_naissance"
                    type="date"
                    required
                    defaultValue={edition?.date_naissance ?? ""}
                  />
                </div>
                <div>
                  <Label htmlFor="relation">Relation *</Label>
                  <select
                    id="relation"
                    name="relation"
                    required
                    defaultValue={edition?.relation ?? "ami"}
                    className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  >
                    {RELATIONS.map((r) => (
                      <option key={r} value={r}>
                        {LABELS_REL[r]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <Label htmlFor="idees_cadeaux">Idées cadeaux</Label>
                <Input
                  id="idees_cadeaux"
                  name="idees_cadeaux"
                  defaultValue={edition?.idees_cadeaux ?? ""}
                />
              </div>
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Input
                  id="notes"
                  name="notes"
                  defaultValue={edition?.notes ?? ""}
                />
              </div>
              <Button type="submit" className="w-full">
                {edition ? "Enregistrer" : "Ajouter"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Prochain */}
      {prochain && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Gift className="h-5 w-5 text-primary" />
              Prochain anniversaire
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg font-semibold">{prochain.nom_personne}</p>
                <p className="text-sm text-muted-foreground">
                  {LABELS_REL[prochain.relation] ?? prochain.relation}
                  {prochain.age != null && ` — ${prochain.age} ans`}
                </p>
              </div>
              <Badge className="text-sm">
                Dans {prochain.jours_restants ?? "?"} jours
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Liste */}
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Tous les anniversaires</h2>
        {isLoading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardContent className="py-4">
                  <div className="h-5 w-32 animate-pulse rounded bg-muted" />
                  <div className="mt-2 h-4 w-20 animate-pulse rounded bg-muted" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : anniversaires.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              <Cake className="h-8 w-8 mx-auto mb-2 opacity-50" />
              Aucun anniversaire enregistré
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {anniversaires.map((a) => (
              <Card key={a.id}>
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex items-center gap-3">
                    <Cake className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{a.nom_personne}</p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(a.date_naissance).toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "long",
                        })}
                        {a.age != null && ` (${a.age} ans)`}
                      </p>
                      {a.idees_cadeaux && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          🎁 {a.idees_cadeaux}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        (a.jours_restants ?? 999) <= 30
                          ? "default"
                          : "secondary"
                      }
                      className="text-xs"
                    >
                      {a.jours_restants ?? "?"}j
                    </Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => ouvrir(a)}
                      aria-label="Modifier l'anniversaire"
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 text-destructive"
                      onClick={() => mutSupprimer.mutate(a.id)}
                      aria-label="Supprimer l'anniversaire"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
