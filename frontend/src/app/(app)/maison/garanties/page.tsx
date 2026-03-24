// ═══════════════════════════════════════════════════════════
// Garanties — Appareils et SAV
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { ShieldCheck, AlertTriangle, Plus, Clock, Pencil, Trash2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerGaranties,
  alertesGaranties,
  statsGaranties,
  creerGarantie,
  modifierGarantie,
  supprimerGarantie,
} from "@/bibliotheque/api/maison";
import type { Garantie } from "@/types/maison";
import { toast } from "sonner";

export default function PageGaranties() {
  const formsVide = { appareil: "", marque: "", date_achat: "", date_fin_garantie: "", piece: "", magasin: "", prix_achat: "" };
  const [form, setForm] = useState(formsVide);
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Garantie>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (g) => setForm({ appareil: g.appareil, marque: g.marque ?? "", date_achat: g.date_achat ?? "", date_fin_garantie: g.date_fin_garantie ?? "", piece: g.piece ?? "", magasin: g.magasin ?? "", prix_achat: g.prix_achat != null ? String(g.prix_achat) : "" }),
    });
  const queryClient = useQueryClient();

  const { data: garanties, isLoading } = utiliserRequete(
    ["maison", "garanties"],
    () => listerGaranties()
  );

  const { data: alertes } = utiliserRequete(
    ["maison", "garanties", "alertes"],
    () => alertesGaranties(60)
  );

  const { data: stats } = utiliserRequete(
    ["maison", "garanties", "stats"],
    () => statsGaranties()
  );

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "garanties"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerGarantie(data as Omit<Garantie, "id">),
    {
      onSuccess: () => { invalider(); fermerDialog(); toast.success("Garantie ajoutée"); },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Garantie> }) => modifierGarantie(id, data),
    {
      onSuccess: () => { invalider(); fermerDialog(); toast.success("Garantie modifiée"); },
      onError: () => toast.error("Erreur lors de la modification"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerGarantie, {
    onSuccess: () => { invalider(); toast.success("Garantie supprimée"); },
    onError: () => toast.error("Erreur lors de la suppression"),
  });



  const soumettre = () => {
    const payload = {
      appareil: form.appareil,
      marque: form.marque || undefined,
      date_achat: form.date_achat,
      date_fin_garantie: form.date_fin_garantie,
      piece: form.piece || undefined,
      magasin: form.magasin || undefined,
      prix_achat: form.prix_achat ? Number(form.prix_achat) : undefined,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">🛡️ Garanties</h1>
          <p className="text-muted-foreground">
            Suivi des garanties et incidents SAV
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
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.actives}</p>
              <p className="text-xs text-muted-foreground">Actives</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold text-destructive">{stats.expirees}</p>
              <p className="text-xs text-muted-foreground">Expirées</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{stats.valeur_totale.toFixed(0)} €</p>
              <p className="text-xs text-muted-foreground">Valeur couverte</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alertes expiration */}
      {alertes && alertes.length > 0 && (
        <Card className="border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <Clock className="h-4 w-4 text-amber-500" />
              Garanties expirant bientôt
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alertes.map((a) => (
                <div key={a.id} className="flex justify-between text-sm">
                  <span>{a.appareil}</span>
                  <Badge variant={a.jours_restants <= 30 ? "destructive" : "secondary"}>
                    {a.jours_restants}j
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Liste garanties */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      ) : !garanties?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <ShieldCheck className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucune garantie enregistrée
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {garanties.map((g) => (
            <Card key={g.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{g.appareil}</CardTitle>
                  <div className="flex items-center gap-1">
                    <Badge
                      variant={g.statut === "active" ? "default" : "secondary"}
                    >
                      {g.statut}
                    </Badge>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(g)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(g.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                {g.marque && (
                  <p className="text-muted-foreground">{g.marque}</p>
                )}
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Achat</span>
                  <span>
                    {new Date(g.date_achat).toLocaleDateString("fr-FR")}
                    {g.prix_achat ? ` — ${g.prix_achat.toFixed(2)} €` : ""}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Fin garantie</span>
                  <span>
                    {new Date(g.date_fin_garantie).toLocaleDateString("fr-FR")}
                  </span>
                </div>
                {g.magasin && (
                  <p className="text-xs text-muted-foreground">{g.magasin}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dialog CRUD */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier la garantie" : "Nouvelle garantie"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
        texteBouton={enEdition ? "Modifier" : "Ajouter"}
      >
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="appareil">Appareil</Label>
            <Input id="appareil" value={form.appareil} onChange={(e) => setForm({ ...form, appareil: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="marque">Marque</Label>
            <Input id="marque" value={form.marque} onChange={(e) => setForm({ ...form, marque: e.target.value })} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="date_achat">Date d'achat</Label>
            <Input id="date_achat" type="date" value={form.date_achat} onChange={(e) => setForm({ ...form, date_achat: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="date_fin_garantie">Fin de garantie</Label>
            <Input id="date_fin_garantie" type="date" value={form.date_fin_garantie} onChange={(e) => setForm({ ...form, date_fin_garantie: e.target.value })} required />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="piece">Pièce</Label>
            <Input id="piece" value={form.piece} onChange={(e) => setForm({ ...form, piece: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="magasin">Magasin</Label>
            <Input id="magasin" value={form.magasin} onChange={(e) => setForm({ ...form, magasin: e.target.value })} />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="prix_achat">Prix d'achat (€)</Label>
          <Input id="prix_achat" type="number" step="0.01" value={form.prix_achat} onChange={(e) => setForm({ ...form, prix_achat: e.target.value })} />
        </div>
      </DialogueFormulaire>
    </div>
  );
}
