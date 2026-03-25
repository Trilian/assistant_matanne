// ═══════════════════════════════════════════════════════════
// Contrats — Assurances, énergie, abonnements
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { FileText, AlertTriangle, Plus, Pencil, Trash2 } from "lucide-react";
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
import { toast } from "sonner";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerContrats,
  alertesContrats,
  resumeFinancierContrats,
  creerContrat,
  modifierContrat,
  supprimerContrat,
} from "@/bibliotheque/api/maison";
import type { Contrat } from "@/types/maison";

export default function PageContrats() {
  const formsVide = { nom: "", type_contrat: "", fournisseur: "", montant_mensuel: "", date_debut: "", date_fin: "", statut: "actif" };
  const [form, setForm] = useState(formsVide);
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Contrat>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (c) => setForm({ nom: c.nom, type_contrat: c.type_contrat, fournisseur: c.fournisseur ?? "", montant_mensuel: c.montant_mensuel != null ? String(c.montant_mensuel) : "", date_debut: c.date_debut ?? "", date_fin: c.date_fin ?? "", statut: c.statut ?? "actif" }),
    });
  const queryClient = useQueryClient();

  const { data: contrats, isLoading } = utiliserRequete(
    ["maison", "contrats"],
    () => listerContrats()
  );

  const { data: alertes } = utiliserRequete(
    ["maison", "contrats", "alertes"],
    () => alertesContrats(60)
  );

  const { data: resume } = utiliserRequete(
    ["maison", "contrats", "resume"],
    () => resumeFinancierContrats()
  );

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "contrats"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerContrat(data as Omit<Contrat, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Contrat ajouté"); } }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Contrat> }) => modifierContrat(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Contrat modifié"); } }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerContrat, { onSuccess: () => { invalider(); toast.success("Contrat supprimé"); } });



  const soumettre = () => {
    const payload = {
      nom: form.nom,
      type_contrat: form.type_contrat,
      fournisseur: form.fournisseur || undefined,
      montant_mensuel: form.montant_mensuel ? Number(form.montant_mensuel) : undefined,
      date_debut: form.date_debut,
      date_fin: form.date_fin || undefined,
      statut: form.statut,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">📄 Contrats</h1>
          <p className="text-muted-foreground">
            Assurances, énergie, abonnements et contrats divers
          </p>
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-2 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Résumé financier */}
      {resume && (
        <div className="grid gap-3 sm:grid-cols-3">
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{resume.total_mensuel.toFixed(0)} €</p>
              <p className="text-xs text-muted-foreground">Par mois</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{resume.total_annuel.toFixed(0)} €</p>
              <p className="text-xs text-muted-foreground">Par an</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4 text-center">
              <p className="text-2xl font-bold">{contrats?.length ?? 0}</p>
              <p className="text-xs text-muted-foreground">Contrats actifs</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alertes renouvellement */}
      {alertes && alertes.length > 0 && (
        <Card className="border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              À renouveler prochainement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alertes.map((a) => (
                <div key={a.id} className="flex justify-between text-sm">
                  <span>
                    {a.nom}{" "}
                    <span className="text-muted-foreground">({a.type_contrat})</span>
                  </span>
                  <Badge variant={a.jours_restants <= 30 ? "destructive" : "secondary"}>
                    {a.jours_restants}j
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Liste contrats */}
      {isLoading ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : !contrats?.length ? (
        <Card>
          <CardContent className="py-10 text-center text-muted-foreground">
            <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
            Aucun contrat enregistré
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {contrats.map((contrat) => (
            <Card key={contrat.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{contrat.nom}</CardTitle>
                  <div className="flex items-center gap-1">
                    <Badge variant="outline">{contrat.type_contrat}</Badge>
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(contrat)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(contrat.id)}>
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                {contrat.fournisseur && (
                  <p className="text-muted-foreground">{contrat.fournisseur}</p>
                )}
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Montant</span>
                  <span className="font-medium">
                    {contrat.montant_mensuel
                      ? `${contrat.montant_mensuel.toFixed(2)} €/mois`
                      : contrat.montant_annuel
                        ? `${contrat.montant_annuel.toFixed(2)} €/an`
                        : "—"}
                  </span>
                </div>
                {contrat.date_fin && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Échéance</span>
                    <span>
                      {new Date(contrat.date_fin).toLocaleDateString("fr-FR")}
                    </span>
                  </div>
                )}
                <div className="flex justify-end mt-1">
                  <Badge
                    variant={contrat.statut === "actif" ? "default" : "secondary"}
                  >
                    {contrat.statut}
                  </Badge>
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
        titre={enEdition ? "Modifier le contrat" : "Nouveau contrat"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
        texteBouton={enEdition ? "Modifier" : "Ajouter"}
      >
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="nom">Nom</Label>
            <Input id="nom" value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="type_contrat">Type</Label>
            <Input id="type_contrat" value={form.type_contrat} onChange={(e) => setForm({ ...form, type_contrat: e.target.value })} required />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="fournisseur">Fournisseur</Label>
            <Input id="fournisseur" value={form.fournisseur} onChange={(e) => setForm({ ...form, fournisseur: e.target.value })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="montant_mensuel">Montant mensuel (€)</Label>
            <Input id="montant_mensuel" type="number" step="0.01" value={form.montant_mensuel} onChange={(e) => setForm({ ...form, montant_mensuel: e.target.value })} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="date_debut">Date début</Label>
            <Input id="date_debut" type="date" value={form.date_debut} onChange={(e) => setForm({ ...form, date_debut: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="date_fin">Date fin</Label>
            <Input id="date_fin" type="date" value={form.date_fin} onChange={(e) => setForm({ ...form, date_fin: e.target.value })} />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="statut">Statut</Label>
          <Input id="statut" value={form.statut} onChange={(e) => setForm({ ...form, statut: e.target.value })} />
        </div>
      </DialogueFormulaire>
    </div>
  );
}
