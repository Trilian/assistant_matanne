// ═══════════════════════════════════════════════════════════
// Dépenses Maison — Suivi des dépenses (CRUD complet)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Banknote,
  Plus,
  Pencil,
  Trash2,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerDepensesMaison,
  creerDepenseMaison,
  modifierDepenseMaison,
  supprimerDepenseMaison,
  statsDepensesMaison,
} from "@/bibliotheque/api/maison";
import type { DepenseMaison } from "@/types/maison";

const CATEGORIES = ["Courses", "Travaux", "Équipement", "Énergie", "Abonnements", "Divers"];

export default function PageDepenses() {
  const [categorie, setCategorie] = useState<string | undefined>();
  const [dialogOuvert, setDialogOuvert] = useState(false);
  const [enEdition, setEnEdition] = useState<DepenseMaison | null>(null);
  const [form, setForm] = useState({
    libelle: "",
    montant: "",
    categorie: "",
    date: new Date().toISOString().slice(0, 10),
    fournisseur: "",
    recurrence: "",
    notes: "",
  });
  const queryClient = useQueryClient();

  const { data: depenses, isLoading } = utiliserRequete(
    ["maison", "depenses", categorie ?? "all"],
    () => listerDepensesMaison()
  );

  const { data: stats } = utiliserRequete(
    ["maison", "depenses", "stats"],
    statsDepensesMaison
  );

  const invalider = () =>
    queryClient.invalidateQueries({ queryKey: ["maison", "depenses"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) =>
      creerDepenseMaison(data as Omit<DepenseMaison, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); } }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<DepenseMaison> }) =>
      modifierDepenseMaison(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); } }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerDepenseMaison, {
    onSuccess: invalider,
  });

  const ouvrirCreation = () => {
    setEnEdition(null);
    setForm({
      libelle: "",
      montant: "",
      categorie: "",
      date: new Date().toISOString().slice(0, 10),
      fournisseur: "",
      recurrence: "",
      notes: "",
    });
    setDialogOuvert(true);
  };

  const ouvrirEdition = (d: DepenseMaison) => {
    setEnEdition(d);
    setForm({
      libelle: d.libelle,
      montant: String(d.montant),
      categorie: d.categorie,
      date: d.date,
      fournisseur: d.fournisseur ?? "",
      recurrence: d.recurrence ?? "",
      notes: d.notes ?? "",
    });
    setDialogOuvert(true);
  };

  const fermerDialog = () => {
    setDialogOuvert(false);
    setEnEdition(null);
  };

  const soumettre = () => {
    const payload = {
      libelle: form.libelle,
      montant: Number(form.montant),
      categorie: form.categorie,
      date: form.date,
      fournisseur: form.fournisseur || undefined,
      recurrence: form.recurrence || undefined,
      notes: form.notes || undefined,
    };
    if (enEdition) {
      modifier({ id: enEdition.id, data: payload });
    } else {
      creer(payload);
    }
  };

  const depensesFiltrees = categorie
    ? depenses?.filter((d) => d.categorie === categorie)
    : depenses;

  const fmt = (n: number) =>
    n.toLocaleString("fr-FR", { style: "currency", currency: "EUR" });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">💸 Dépenses</h1>
          <p className="text-muted-foreground">
            Suivi des dépenses maison par catégorie
          </p>
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-2 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid gap-3 sm:grid-cols-4">
          <Card className="border-primary/30 bg-primary/5">
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{fmt(stats.total_mois)}</p>
              <p className="text-xs text-muted-foreground">Ce mois</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{fmt(stats.total_annee)}</p>
              <p className="text-xs text-muted-foreground">Cette année</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{fmt(stats.moyenne_mensuelle)}</p>
              <p className="text-xs text-muted-foreground">Moyenne / mois</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <div className="flex items-center justify-center gap-1">
                {stats.delta_mois_precedent > 0 ? (
                  <TrendingUp className="h-4 w-4 text-destructive" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-green-500" />
                )}
                <p className="text-2xl font-bold">
                  {stats.delta_mois_precedent > 0 ? "+" : ""}
                  {stats.delta_mois_precedent.toFixed(0)} %
                </p>
              </div>
              <p className="text-xs text-muted-foreground">vs mois précédent</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Répartition par catégorie */}
      {stats && Object.keys(stats.par_categorie).length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Répartition par catégorie</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(stats.par_categorie)
                .sort(([, a], [, b]) => b - a)
                .map(([cat, montant]) => {
                  const pct = stats.total_mois > 0 ? (montant / stats.total_mois) * 100 : 0;
                  return (
                    <div key={cat} className="flex items-center gap-2">
                      <span className="text-sm w-28 truncate">{cat}</span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full"
                          style={{ width: `${Math.min(pct, 100)}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium w-20 text-right">
                        {fmt(montant)}
                      </span>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filtres catégorie */}
      <div className="flex gap-2 flex-wrap">
        <Button
          variant={!categorie ? "default" : "outline"}
          size="sm"
          onClick={() => setCategorie(undefined)}
        >
          Toutes
        </Button>
        {CATEGORIES.map((cat) => (
          <Button
            key={cat}
            variant={categorie === cat ? "default" : "outline"}
            size="sm"
            onClick={() => setCategorie(cat)}
          >
            {cat}
          </Button>
        ))}
      </div>

      {/* Liste dépenses */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      ) : !depensesFiltrees?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <Banknote className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucune dépense enregistrée
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {depensesFiltrees.map((d) => (
            <Card key={d.id}>
              <CardContent className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div>
                    <p className="font-medium text-sm">{d.libelle}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Badge variant="outline" className="text-xs">{d.categorie}</Badge>
                      <span className="text-xs text-muted-foreground">{d.date}</span>
                      {d.fournisseur && (
                        <span className="text-xs text-muted-foreground">· {d.fournisseur}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold">{fmt(d.montant)}</span>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(d)}>
                    <Pencil className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(d.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
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
        titre={enEdition ? "Modifier la dépense" : "Nouvelle dépense"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
      >
        <div className="space-y-3">
          <div className="space-y-1">
            <Label>Libellé *</Label>
            <Input value={form.libelle} onChange={(e) => setForm({ ...form, libelle: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Montant (€) *</Label>
              <Input type="number" step="0.01" min="0" value={form.montant} onChange={(e) => setForm({ ...form, montant: e.target.value })} />
            </div>
            <div className="space-y-1">
              <Label>Date *</Label>
              <Input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Catégorie *</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={form.categorie}
              onChange={(e) => setForm({ ...form, categorie: e.target.value })}
            >
              <option value="">Choisir…</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <Label>Fournisseur</Label>
            <Input value={form.fournisseur} onChange={(e) => setForm({ ...form, fournisseur: e.target.value })} />
          </div>
          <div className="space-y-1">
            <Label>Récurrence</Label>
            <select
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
              value={form.recurrence}
              onChange={(e) => setForm({ ...form, recurrence: e.target.value })}
            >
              <option value="">Ponctuel</option>
              <option value="mensuel">Mensuel</option>
              <option value="trimestriel">Trimestriel</option>
              <option value="annuel">Annuel</option>
            </select>
          </div>
          <div className="space-y-1">
            <Label>Notes</Label>
            <Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}
