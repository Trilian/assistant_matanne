// ═══════════════════════════════════════════════════════════
// Anniversaires — Dates importantes (connecté API)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Cake, Gift, Calendar, Plus, Trash2, Pencil, Sparkles, Loader2, ShoppingCart, Check } from "lucide-react";
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
  obtenirSuggestionsAchatsIA,
  obtenirChecklistAnniversaireAuto,
  synchroniserChecklistAnniversaireAuto,
  mettreAJourItemChecklist,
  itemChecklistVersAchat,
  type ChecklistAnniversaire,
  type ChecklistAnniversairePreview,
  type Anniversaire,
  type SuggestionAchat,
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
  const [suggestionsOuvert, setSuggestionsOuvert] = useState(false);
  const [suggestions, setSuggestions] = useState<SuggestionAchat[]>([]);
  const [anniversairePourSuggestion, setAnniversairePourSuggestion] = useState<Anniversaire | null>(null);
  const [checklistPreview, setChecklistPreview] = useState<ChecklistAnniversairePreview | null>(null);
  const [checklistActive, setChecklistActive] = useState<ChecklistAnniversaire | null>(null);

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

  const mutSuggestions = utiliserMutation(
    (a: Anniversaire) =>
      obtenirSuggestionsAchatsIA({
        type: "anniversaire",
        nom: a.nom_personne,
        age: a.age ?? undefined,
        relation: a.relation,
        budget_max: 50,
      }),
    {
      onSuccess: (data, a) => {
        setSuggestions(data.suggestions);
        setAnniversairePourSuggestion(a);
        setSuggestionsOuvert(true);
      },
      onError: () => toast.error("Impossible de générer les suggestions"),
    }
  );

  const mutChecklistPreview = utiliserMutation(
    (a: Anniversaire) => obtenirChecklistAnniversaireAuto(a.id),
    {
      onSuccess: (data) => {
        setChecklistPreview(data);
        toast.success("Aperçu checklist généré");
      },
      onError: () => toast.error("Impossible de générer l'aperçu checklist"),
    }
  );

  const mutChecklistSync = utiliserMutation(
    (a: Anniversaire) => synchroniserChecklistAnniversaireAuto(a.id),
    {
      onSuccess: (data) => {
        setChecklistActive(data);
        toast.success("Checklist synchronisée (auto + manuel)");
      },
      onError: () => toast.error("Impossible de synchroniser la checklist"),
    }
  );

  const mutToggleItem = utiliserMutation(
    ({ checklistId, itemId, fait }: { checklistId: number; itemId: number; fait: boolean }) =>
      mettreAJourItemChecklist(checklistId, itemId, fait),
    {
      onSuccess: (updatedItem) => {
        setChecklistActive((prev) => {
          if (!prev) return prev;
          const updated = { ...prev };
          const cat = updatedItem.categorie;
          if (updated.items_par_categorie[cat]) {
            updated.items_par_categorie = {
              ...updated.items_par_categorie,
              [cat]: updated.items_par_categorie[cat].map((it) =>
                it.id === updatedItem.id ? updatedItem : it
              ),
            };
          }
          const tousLesItems = Object.values(updated.items_par_categorie).flat();
          updated.items_faits = tousLesItems.filter((it) => it.fait).length;
          updated.items_total = tousLesItems.length;
          updated.taux_completion =
            updated.items_total > 0
              ? Math.round((updated.items_faits / updated.items_total) * 100)
              : 0;
          return updated;
        });
      },
      onError: () => toast.error("Impossible de mettre à jour l'item"),
    }
  );

  const mutVersAchat = utiliserMutation(
    ({ checklistId, itemId }: { checklistId: number; itemId: number }) =>
      itemChecklistVersAchat(checklistId, itemId),
    {
      onSuccess: () => toast.success("Item envoyé vers les achats ✓"),
      onError: () => toast.error("Impossible d'envoyer vers les achats"),
    }
  );

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
              <div className="flex items-center gap-2">
                <Badge className="text-sm">
                  Dans {prochain.jours_restants ?? "?"} jours
                </Badge>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => mutChecklistPreview.mutate(prochain)}
                  disabled={mutChecklistPreview.isPending}
                >
                  {mutChecklistPreview.isPending ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                  ) : (
                    <Sparkles className="h-3.5 w-3.5 mr-1" />
                  )}
                  Aperçu checklist
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => mutChecklistSync.mutate(prochain)}
                  disabled={mutChecklistSync.isPending}
                >
                  {mutChecklistSync.isPending ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                  ) : (
                    <Gift className="h-3.5 w-3.5 mr-1" />
                  )}
                  Synchroniser checklist
                </Button>
                {(prochain.jours_restants ?? 999) <= 14 && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => mutSuggestions.mutate(prochain)}
                    disabled={mutSuggestions.isPending}
                  >
                    {mutSuggestions.isPending ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                    ) : (
                      <Sparkles className="h-3.5 w-3.5 mr-1" />
                    )}
                    Idées cadeaux IA
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {(checklistPreview || checklistActive) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Gift className="h-5 w-5 text-primary" />
              Checklist anniversaire intelligente
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {checklistPreview && (
              <div className="rounded-md border p-3 bg-muted/30">
                <p className="text-sm font-medium">Aperçu auto ({checklistPreview.profil})</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Budget suggéré: {checklistPreview.budget_total_suggere.toFixed(0)} €
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {Array.from(new Set(checklistPreview.items_auto.map((i) => i.categorie))).map((cat) => (
                    <Badge key={cat} variant="secondary" className="text-xs">{cat}</Badge>
                  ))}
                </div>
              </div>
            )}

            {checklistActive && (
              <div className="rounded-md border p-3 space-y-4">
                <div>
                  <p className="text-sm font-medium">{checklistActive.nom}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Budget: {checklistActive.budget_depense.toFixed(0)} € / {(checklistActive.budget_total ?? 0).toFixed(0)} €
                  </p>
                  {/* Barre de progression globale */}
                  <div className="mt-2">
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                      <span>Progression globale</span>
                      <span>{checklistActive.items_faits}/{checklistActive.items_total} ({checklistActive.taux_completion}%)</span>
                    </div>
                    <div className="h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all"
                        style={{ width: `${checklistActive.taux_completion}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Items par catégorie */}
                {Object.entries(checklistActive.items_par_categorie).map(([categorie, items]) => {
                  const itemsFaits = items.filter((it) => it.fait).length;
                  const pctCat = items.length > 0 ? Math.round((itemsFaits / items.length) * 100) : 0;
                  return (
                    <div key={categorie} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary" className="text-xs capitalize">{categorie}</Badge>
                        <span className="text-xs text-muted-foreground">{itemsFaits}/{items.length}</span>
                      </div>
                      {/* Barre de progression par catégorie */}
                      <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-primary/70 rounded-full transition-all"
                          style={{ width: `${pctCat}%` }}
                        />
                      </div>
                      {/* Liste des items */}
                      <div className="space-y-1.5 pl-1">
                        {items.map((item) => (
                          <div
                            key={item.id}
                            className="flex items-center gap-2 rounded p-1.5 hover:bg-muted/40 transition-colors"
                          >
                            {/* Checkbox */}
                            <button
                              type="button"
                              aria-label={item.fait ? "Marquer comme non fait" : "Marquer comme fait"}
                              className={`flex-shrink-0 h-4 w-4 rounded border flex items-center justify-center transition-colors ${
                                item.fait ? "bg-primary border-primary" : "border-muted-foreground/40"
                              }`}
                              onClick={() =>
                                mutToggleItem.mutate({
                                  checklistId: checklistActive.id,
                                  itemId: item.id,
                                  fait: !item.fait,
                                })
                              }
                            >
                              {item.fait && <Check className="h-2.5 w-2.5 text-primary-foreground" />}
                            </button>
                            {/* Nom + infos */}
                            <div className="flex-1 min-w-0">
                              <span className={`text-sm ${item.fait ? "line-through text-muted-foreground" : ""}`}>
                                {item.libelle}
                              </span>
                              <div className="flex items-center gap-2 mt-0.5">
                                {item.budget_estime != null && (
                                  <span className="text-xs text-muted-foreground">~{item.budget_estime.toFixed(0)} €</span>
                                )}
                                <Badge
                                  variant={item.source === "auto" ? "secondary" : "outline"}
                                  className="text-xs py-0 h-4"
                                >
                                  {item.source === "auto" ? "auto" : "manuel"}
                                </Badge>
                              </div>
                            </div>
                            {/* Bouton → Achats */}
                            {!item.fait && (
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-7 px-2 text-xs flex-shrink-0"
                                aria-label="Envoyer vers les achats"
                                disabled={mutVersAchat.isPending}
                                onClick={() =>
                                  mutVersAchat.mutate({
                                    checklistId: checklistActive.id,
                                    itemId: item.id,
                                  })
                                }
                              >
                                <ShoppingCart className="h-3 w-3 mr-1" />
                                → Achats
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Dialog suggestions IA */}
      <Dialog open={suggestionsOuvert} onOpenChange={setSuggestionsOuvert}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              🎁 Idées cadeaux pour {anniversairePourSuggestion?.nom_personne}
            </DialogTitle>
          </DialogHeader>
          {suggestions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">Aucune suggestion générée.</p>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {suggestions.map((s, i) => (
                <div key={i} className="rounded-md border p-3 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-sm">{s.titre}</p>
                    {s.fourchette_prix && (
                      <Badge variant="secondary" className="text-xs">{s.fourchette_prix}</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{s.description}</p>
                  {s.ou_acheter && (
                    <p className="text-xs text-muted-foreground">📍 {s.ou_acheter}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>

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
