// ═══════════════════════════════════════════════════════════
// Garanties — Suivi des garanties appareils
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  ShieldCheck, Plus, Pencil, Trash2, AlertTriangle, Euro,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerGaranties, alertesGaranties, statsGaranties,
  creerGarantie, modifierGarantie, supprimerGarantie,
} from "@/bibliotheque/api/maison";
import type { Garantie } from "@/types/maison";
import { toast } from "sonner";

// ─── Constantes ──────────────────────────────────────────────

const PIECES = [
  "Cuisine", "Salon", "Chambre", "Salle de bain", "Buanderie",
  "Bureau", "Garage", "Cave", "Autre",
];

const STATUT_COULEUR: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  expiree: "bg-red-100 text-red-700",
  bientot: "bg-amber-100 text-amber-700",
};

// ─── Carte Garantie ───────────────────────────────────────────

function CarteGarantie({
  garantie: g,
  onEdit,
  onDelete,
}: {
  garantie: Garantie;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const maintenant = new Date();
  const dateFin = g.date_fin_garantie ? new Date(g.date_fin_garantie) : null;
  const joursRestants = dateFin
    ? Math.ceil((dateFin.getTime() - maintenant.getTime()) / (1000 * 60 * 60 * 24))
    : null;
  const statut =
    joursRestants === null ? "active"
    : joursRestants < 0 ? "expiree"
    : joursRestants <= 90 ? "bientot"
    : "active";

  return (
    <Card className={statut === "bientot" ? "border-amber-300" : statut === "expiree" ? "border-red-200" : ""}>
      <CardContent className="py-3">
        <div className="flex items-start gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <p className="text-sm font-medium">{g.appareil}</p>
              {g.marque && (
                <span className="text-xs text-muted-foreground">{g.marque}</span>
              )}
              {statut !== "active" && (
                <Badge className={`text-[10px] ${STATUT_COULEUR[statut]}`}>
                  {statut === "expiree" ? "Expirée" : `Expire dans ${joursRestants} j`}
                </Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1">
              {g.piece && (
                <span className="text-xs text-muted-foreground">{g.piece}</span>
              )}
              {g.magasin && (
                <span className="text-xs text-muted-foreground">{g.magasin}</span>
              )}
              {g.date_achat && (
                <span className="text-xs text-muted-foreground">
                  Acheté le {new Date(g.date_achat).toLocaleDateString("fr-FR")}
                </span>
              )}
              {g.date_fin_garantie && (
                <span className="text-xs text-muted-foreground">
                  Garantie jusqu'au {new Date(g.date_fin_garantie).toLocaleDateString("fr-FR")}
                </span>
              )}
              {g.prix_achat != null && (
                <span className="text-xs text-muted-foreground flex items-center gap-0.5">
                  <Euro className="h-3 w-3" />{g.prix_achat} €
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onEdit}>
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive"
              onClick={onDelete}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Page principale ──────────────────────────────────────────

export default function PageGaranties() {
  const queryClient = useQueryClient();

  const formVide = {
    appareil: "", marque: "", date_achat: "", date_fin_garantie: "",
    piece: "", magasin: "", prix_achat: "", notes: "",
  };
  const [form, setForm] = useState(formVide);

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Garantie>({
      onOuvrirCreation: () => setForm(formVide),
      onOuvrirEdition: (g) =>
        setForm({
          appareil: g.appareil ?? "",
          marque: g.marque ?? "",
          date_achat: g.date_achat ?? "",
          date_fin_garantie: g.date_fin_garantie ?? "",
          piece: g.piece ?? "",
          magasin: g.magasin ?? "",
          prix_achat: g.prix_achat != null ? String(g.prix_achat) : "",
          notes: g.notes ?? "",
        }),
    });

  const { data: garanties, isLoading } = utiliserRequete(
    ["maison", "garanties"],
    () => listerGaranties()
  );
  const { data: alertes } = utiliserRequete(
    ["maison", "garanties", "alertes"],
    () => alertesGaranties(90)
  );
  const { data: stats } = utiliserRequete(
    ["maison", "garanties", "stats"],
    statsGaranties
  );

  const invalider = () =>
    queryClient.invalidateQueries({ queryKey: ["maison", "garanties"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Omit<Garantie, "id">) => creerGarantie(data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Garantie ajoutée"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Garantie> }) => modifierGarantie(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Garantie modifiée"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerGarantie, {
    onSuccess: () => { invalider(); toast.success("Garantie supprimée"); },
  });

  const soumettre = () => {
    const payload = {
      appareil: form.appareil,
      marque: form.marque || undefined,
      date_achat: form.date_achat || undefined,
      date_fin_garantie: form.date_fin_garantie,
      piece: form.piece || undefined,
      magasin: form.magasin || undefined,
      prix_achat: form.prix_achat ? Number(form.prix_achat) : undefined,
      notes: form.notes || undefined,
      statut: "active",
    } as Omit<Garantie, "id">;
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-primary" />
          Garanties
        </h1>
        <p className="text-muted-foreground">Suivi des garanties de vos appareils</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.actives}</p>
              <p className="text-xs text-muted-foreground">Actives</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold text-red-500">{stats.expirees}</p>
              <p className="text-xs text-muted-foreground">Expirées</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-2xl font-bold">{stats.valeur_totale?.toLocaleString("fr-FR")} €</p>
              <p className="text-xs text-muted-foreground">Valeur couverte</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alertes */}
      {alertes && alertes.length > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4" />
              {alertes.length} garantie(s) expirant dans 90 jours
            </p>
            {alertes.slice(0, 3).map((a) => (
              <p key={a.id} className="text-xs text-muted-foreground mt-0.5 ml-5">
                • {a.appareil} — {new Date(a.date_fin_garantie).toLocaleDateString("fr-FR")}
                {" "}({a.jours_restants} j)
              </p>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-1.5 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Liste */}
      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
      ) : !garanties?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <ShieldCheck className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="font-medium">Aucune garantie enregistrée</p>
            <p className="text-xs mt-1">Ajoutez vos appareils pour suivre leurs garanties</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {garanties.map((g) => (
            <CarteGarantie
              key={g.id}
              garantie={g}
              onEdit={() => ouvrirEdition(g)}
              onDelete={() => supprimer(g.id)}
            />
          ))}
        </div>
      )}

      {/* Formulaire */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier la garantie" : "Nouvelle garantie"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
      >
        <div className="space-y-3">
          <div className="space-y-1">
            <Label htmlFor="appareil">Appareil *</Label>
            <Input
              id="appareil"
              value={form.appareil}
              onChange={(e) => setForm((f) => ({ ...f, appareil: e.target.value }))}
              placeholder="ex: Lave-linge, Réfrigérateur…"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="marque">Marque</Label>
              <Input
                id="marque"
                value={form.marque}
                onChange={(e) => setForm((f) => ({ ...f, marque: e.target.value }))}
                placeholder="ex: Samsung"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="magasin">Magasin</Label>
              <Input
                id="magasin"
                value={form.magasin}
                onChange={(e) => setForm((f) => ({ ...f, magasin: e.target.value }))}
                placeholder="ex: Darty"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="date_achat">Date d&apos;achat</Label>
              <Input
                id="date_achat"
                type="date"
                value={form.date_achat}
                onChange={(e) => setForm((f) => ({ ...f, date_achat: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="date_fin_garantie">Fin de garantie</Label>
              <Input
                id="date_fin_garantie"
                type="date"
                value={form.date_fin_garantie}
                onChange={(e) => setForm((f) => ({ ...f, date_fin_garantie: e.target.value }))}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="piece">Pièce</Label>
              <Input
                id="piece"
                value={form.piece}
                onChange={(e) => setForm((f) => ({ ...f, piece: e.target.value }))}
                list="pieces-list"
                placeholder="ex: Cuisine"
              />
              <datalist id="pieces-list">
                {PIECES.map((p) => <option key={p} value={p} />)}
              </datalist>
            </div>
            <div className="space-y-1">
              <Label htmlFor="prix_achat">Prix d&apos;achat (€)</Label>
              <Input
                id="prix_achat"
                type="number"
                min="0"
                step="0.01"
                value={form.prix_achat}
                onChange={(e) => setForm((f) => ({ ...f, prix_achat: e.target.value }))}
                placeholder="ex: 599"
              />
            </div>
          </div>
          <div className="space-y-1">
            <Label htmlFor="notes">Notes</Label>
            <Input
              id="notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              placeholder="Numéro de série, contact SAV…"
            />
          </div>
        </div>
      </DialogueFormulaire>
    </div>
  );
}

