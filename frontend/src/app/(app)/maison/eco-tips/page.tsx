// ═══════════════════════════════════════════════════════════
// Éco-Tips — Actions écologiques
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Leaf, Plus, Filter, Pencil, Trash2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import { listerEcoTips, creerEcoTip, modifierEcoTip, supprimerEcoTip } from "@/bibliotheque/api/maison";
import type { ActionEcologique } from "@/types/maison";
import { toast } from "sonner";

export default function PageEcoTips() {
  const [actifOnly, setActifOnly] = useState(false);
  const formsVide = { titre: "", description: "", categorie: "", impact: "", economie_estimee: "", actif: true };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<ActionEcologique>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (a) => setForm({
        titre: a.titre,
        description: a.description ?? "",
        categorie: a.categorie ?? "",
        impact: a.impact ?? "",
        economie_estimee: a.economie_estimee != null ? String(a.economie_estimee) : "",
        actif: a.actif,
      }),
    });

  const { data: actions, isLoading } = utiliserRequete(
    ["maison", "eco-tips", String(actifOnly)],
    () => listerEcoTips(actifOnly)
  );

  const nbActives = actions?.filter((a) => a.actif).length ?? 0;

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "eco-tips"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerEcoTip(data as Omit<ActionEcologique, "id">),
    {
      onSuccess: () => { invalider(); fermerDialog(); toast.success("Éco-geste ajouté"); },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<ActionEcologique> }) => modifierEcoTip(id, data),
    {
      onSuccess: () => { invalider(); fermerDialog(); toast.success("Éco-geste modifié"); },
      onError: () => toast.error("Erreur lors de la modification"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerEcoTip, {
    onSuccess: () => { invalider(); toast.success("Éco-geste supprimé"); },
    onError: () => toast.error("Erreur lors de la suppression"),
  });

  const soumettre = () => {
    const payload = {
      titre: form.titre,
      description: form.description || undefined,
      categorie: form.categorie || undefined,
      impact: form.impact || undefined,
      economie_estimee: form.economie_estimee ? Number(form.economie_estimee) : undefined,
      actif: form.actif,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🌿 Éco-Tips</h1>
          <p className="text-muted-foreground">
            {nbActives} action(s) écologique(s) en cours
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={actifOnly ? "default" : "outline"}
            size="sm"
            onClick={() => setActifOnly(!actifOnly)}
          >
            <Filter className="mr-2 h-3 w-3" />
            {actifOnly ? "Toutes" : "Actives"}
          </Button>
          <Button size="sm" onClick={ouvrirCreation}>
            <Plus className="mr-2 h-4 w-4" />
            Ajouter
          </Button>
        </div>
      </div>

      {/* Liste actions */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : !actions?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Leaf className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucune action écologique enregistrée
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {actions.map((action) => (
            <Card key={action.id} className={action.actif ? "" : "opacity-60"}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{action.titre}</CardTitle>
                  <div className="flex items-center gap-1">
                    <Badge variant={action.actif ? "default" : "secondary"}>
                      {action.actif ? "Active" : "Inactive"}
                    </Badge>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(action)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(action.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1">
                {action.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {action.description}
                  </p>
                )}
                <div className="flex gap-2 flex-wrap mt-2">
                  {action.categorie && (
                    <Badge variant="outline" className="text-xs">
                      {action.categorie}
                    </Badge>
                  )}
                  {action.impact && (
                    <Badge variant="outline" className="text-xs">
                      Impact: {action.impact}
                    </Badge>
                  )}
                  {action.economie_estimee != null && (
                    <Badge variant="outline" className="text-xs text-green-600">
                      ~{action.economie_estimee} €/an
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dialog CRUD */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier l'action" : "Nouvelle action écologique"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
        texteBouton={enEdition ? "Modifier" : "Ajouter"}
      >
        <div className="space-y-2">
          <Label htmlFor="titre">Titre</Label>
          <Input id="titre" value={form.titre} onChange={(e) => setForm({ ...form, titre: e.target.value })} required />
        </div>
        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Input id="description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="categorie">Catégorie</Label>
            <Input id="categorie" value={form.categorie} onChange={(e) => setForm({ ...form, categorie: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="impact">Impact</Label>
            <Input id="impact" value={form.impact} onChange={(e) => setForm({ ...form, impact: e.target.value })} />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="economie_estimee">Économie estimée (€/an)</Label>
          <Input id="economie_estimee" type="number" step="0.01" value={form.economie_estimee} onChange={(e) => setForm({ ...form, economie_estimee: e.target.value })} />
        </div>
        <div className="flex items-center gap-2">
          <input id="actif" type="checkbox" checked={form.actif} onChange={(e) => setForm({ ...form, actif: e.target.checked })} className="h-4 w-4" />
          <Label htmlFor="actif">Active</Label>
        </div>
      </DialogueFormulaire>
    </div>
  );
}
