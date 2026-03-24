// ═══════════════════════════════════════════════════════════
// Diagnostics — Diagnostics immobiliers et estimations
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { ClipboardCheck, AlertTriangle, Plus, TrendingUp, Pencil, Trash2 } from "lucide-react";
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
  listerDiagnostics,
  alertesDiagnostics,
  listerEstimations,
  derniereEstimation,
  creerDiagnostic,
  modifierDiagnostic,
  supprimerDiagnostic,
} from "@/bibliotheque/api/maison";
import type { DiagnosticImmobilier } from "@/types/maison";
import { toast } from "sonner";

export default function PageDiagnostics() {
  const formsVide = { type_diagnostic: "", date_realisation: "", date_expiration: "", resultat: "", diagnostiqueur: "" };
  const [form, setForm] = useState(formsVide);
  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<DiagnosticImmobilier>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (d) => setForm({ type_diagnostic: d.type_diagnostic, date_realisation: d.date_realisation ?? "", date_expiration: d.date_expiration ?? "", resultat: d.resultat ?? "", diagnostiqueur: d.diagnostiqueur ?? "" }),
    });
  const queryClient = useQueryClient();

  const { data: diagnostics, isLoading } = utiliserRequete(
    ["maison", "diagnostics"],
    () => listerDiagnostics()
  );

  const { data: alertes } = utiliserRequete(
    ["maison", "diagnostics", "alertes"],
    () => alertesDiagnostics(90)
  );

  const { data: estimation } = utiliserRequete(
    ["maison", "estimation", "derniere"],
    () => derniereEstimation()
  );

  const { data: estimations } = utiliserRequete(
    ["maison", "estimations"],
    () => listerEstimations()
  );

  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "diagnostics"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerDiagnostic(data as Omit<DiagnosticImmobilier, "id">),
    {
      onSuccess: () => { invalider(); fermerDialog(); toast.success("Diagnostic ajouté"); },
      onError: () => toast.error("Erreur lors de l'ajout"),
    }
  );

  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<DiagnosticImmobilier> }) => modifierDiagnostic(id, data),
    {
      onSuccess: () => { invalider(); fermerDialog(); toast.success("Diagnostic modifié"); },
      onError: () => toast.error("Erreur lors de la modification"),
    }
  );

  const { mutate: supprimer } = utiliserMutation(supprimerDiagnostic, {
    onSuccess: () => { invalider(); toast.success("Diagnostic supprimé"); },
    onError: () => toast.error("Erreur lors de la suppression"),
  });



  const soumettre = () => {
    const payload = {
      type_diagnostic: form.type_diagnostic,
      date_realisation: form.date_realisation,
      date_expiration: form.date_expiration || undefined,
      resultat: form.resultat || undefined,
      diagnostiqueur: form.diagnostiqueur || undefined,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            📋 Diagnostics & Estimations
          </h1>
          <p className="text-muted-foreground">
            DPE, amiante, plomb, estimations immobilières
          </p>
        </div>
        <Button size="sm" onClick={ouvrirCreation}>
          <Plus className="mr-2 h-4 w-4" />
          Ajouter
        </Button>
      </div>

      {/* Estimation immobilière */}
      {estimation && (
        <Card className="border-primary/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              Dernière estimation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {estimation.valeur_estimee.toLocaleString("fr-FR")} €
            </p>
            <p className="text-sm text-muted-foreground">
              {new Date(estimation.date).toLocaleDateString("fr-FR")}
              {estimation.source ? ` — ${estimation.source}` : ""}
              {estimation.prix_m2 ? ` — ${estimation.prix_m2.toFixed(0)} €/m²` : ""}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Alertes validité */}
      {alertes && alertes.length > 0 && (
        <Card className="border-amber-500/30">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              Diagnostics à renouveler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alertes.map((d) => (
                <div key={d.id} className="flex justify-between text-sm">
                  <span>{d.type_diagnostic}</span>
                  {d.date_expiration && (
                    <span className="text-muted-foreground">
                      {new Date(d.date_expiration).toLocaleDateString("fr-FR")}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Liste diagnostics */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Diagnostics immobiliers</h2>
        {isLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-28" />
            ))}
          </div>
        ) : !diagnostics?.length ? (
          <Card>
            <CardContent className="py-10 text-center text-muted-foreground">
              <ClipboardCheck className="h-8 w-8 mx-auto mb-2 opacity-50" />
              Aucun diagnostic enregistré
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {diagnostics.map((diag) => (
              <Card key={diag.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">
                      {diag.type_diagnostic}
                    </CardTitle>
                    <div className="flex items-center gap-1">
                      {diag.resultat && (
                        <Badge variant="outline">{diag.resultat}</Badge>
                      )}
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(diag)}>
                        <Pencil className="h-3 w-3" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => supprimer(diag.id)}>
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Réalisé le</span>
                    <span>
                      {new Date(diag.date_realisation).toLocaleDateString("fr-FR")}
                    </span>
                  </div>
                  {diag.date_expiration && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Expire le</span>
                      <span>
                        {new Date(diag.date_expiration).toLocaleDateString("fr-FR")}
                      </span>
                    </div>
                  )}
                  {diag.diagnostiqueur && (
                    <p className="text-xs text-muted-foreground">
                      {diag.diagnostiqueur}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Historique estimations */}
      {estimations && estimations.length > 1 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Historique estimations</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {estimations.map((e) => (
              <Card key={e.id}>
                <CardContent className="pt-4">
                  <p className="text-xl font-bold">
                    {e.valeur_estimee.toLocaleString("fr-FR")} €
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {new Date(e.date).toLocaleDateString("fr-FR")}
                    {e.source ? ` — ${e.source}` : ""}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Dialog CRUD */}
      <DialogueFormulaire
        ouvert={dialogOuvert}
        onClose={fermerDialog}
        titre={enEdition ? "Modifier le diagnostic" : "Nouveau diagnostic"}
        onSubmit={soumettre}
        enCours={enCreation || enModif}
        texteBouton={enEdition ? "Modifier" : "Ajouter"}
      >
        <div className="space-y-2">
          <Label htmlFor="type_diagnostic">Type de diagnostic</Label>
          <Input id="type_diagnostic" value={form.type_diagnostic} onChange={(e) => setForm({ ...form, type_diagnostic: e.target.value })} required />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label htmlFor="date_realisation">Date de réalisation</Label>
            <Input id="date_realisation" type="date" value={form.date_realisation} onChange={(e) => setForm({ ...form, date_realisation: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="date_expiration">Date d'expiration</Label>
            <Input id="date_expiration" type="date" value={form.date_expiration} onChange={(e) => setForm({ ...form, date_expiration: e.target.value })} />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="resultat">Résultat</Label>
          <Input id="resultat" value={form.resultat} onChange={(e) => setForm({ ...form, resultat: e.target.value })} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="diagnostiqueur">Diagnostiqueur</Label>
          <Input id="diagnostiqueur" value={form.diagnostiqueur} onChange={(e) => setForm({ ...form, diagnostiqueur: e.target.value })} />
        </div>
      </DialogueFormulaire>
    </div>
  );
}
