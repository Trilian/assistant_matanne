// Page Abonnements — Comparateur d'abonnements maison

"use client";

import { Suspense, useState } from "react";
import { Plus, Trash2, Pencil, Receipt, TrendingDown } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import { SwipeableItem } from "@/composants/swipeable-item";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerAbonnements, creerAbonnement, modifierAbonnement, supprimerAbonnement,
  resumeAbonnements,
} from "@/bibliotheque/api/maison";
import type { Abonnement } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";

const TYPES_ABONNEMENT = [
  { valeur: "eau", label: "Eau" },
  { valeur: "electricite", label: "Électricité" },
  { valeur: "gaz", label: "Gaz" },
  { valeur: "assurance_habitation", label: "Assurance habitation" },
  { valeur: "assurance_auto", label: "Assurance auto" },
  { valeur: "chaudiere", label: "Chaudière" },
  { valeur: "telephone", label: "Téléphone" },
  { valeur: "internet", label: "Internet" },
];

function ContenuAbonnements() {
  const formsVide = { type_abonnement: "", fournisseur: "", prix_mensuel: "", date_debut: "", date_fin_engagement: "", notes: "" };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Abonnement>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (a) => setForm({
        type_abonnement: a.type_abonnement,
        fournisseur: a.fournisseur,
        prix_mensuel: a.prix_mensuel?.toString() ?? "",
        date_debut: a.date_debut ?? "",
        date_fin_engagement: a.date_fin_engagement ?? "",
        notes: a.notes ?? "",
      }),
    });

  const { data: abonnements, isLoading } = utiliserRequete(["maison", "abonnements"], listerAbonnements);
  const { data: resume } = utiliserRequete(["maison", "abonnements", "resume"], resumeAbonnements);
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "abonnements"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerAbonnement(data as Omit<Abonnement, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Abonnement ajouté"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Abonnement> }) => modifierAbonnement(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Abonnement modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerAbonnement, { onSuccess: () => { invalider(); toast.success("Abonnement supprimé"); } });
  const { planifierSuppression } = utiliserSuppressionAnnulable();

  const supprimerAvecUndo = (a: Abonnement) => {
    planifierSuppression(`abo-${a.id}`, {
      libelle: `${a.fournisseur} (${a.type_abonnement})`,
      onConfirmer: () => supprimer(a.id),
      onErreur: () => toast.error("Erreur lors de la suppression"),
    });
  };

  const soumettre = () => {
    const payload = {
      type_abonnement: form.type_abonnement,
      fournisseur: form.fournisseur,
      prix_mensuel: form.prix_mensuel ? parseFloat(form.prix_mensuel) : undefined,
      date_debut: form.date_debut || undefined,
      date_fin_engagement: form.date_fin_engagement || undefined,
      notes: form.notes || undefined,
    };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload as Record<string, unknown>);
  };

  const CHAMPS = [
    { id: "type_abonnement", label: "Type", type: "select" as const, value: form.type_abonnement, onChange: (v: string) => setForm(f => ({ ...f, type_abonnement: v })), required: true, options: TYPES_ABONNEMENT },
    { id: "fournisseur", label: "Fournisseur", type: "text" as const, value: form.fournisseur, onChange: (v: string) => setForm(f => ({ ...f, fournisseur: v })), required: true },
    { id: "prix_mensuel", label: "Prix mensuel (€)", type: "number" as const, value: form.prix_mensuel, onChange: (v: string) => setForm(f => ({ ...f, prix_mensuel: v })) },
    { id: "date_debut", label: "Date de début", type: "date" as const, value: form.date_debut, onChange: (v: string) => setForm(f => ({ ...f, date_debut: v })) },
    { id: "date_fin_engagement", label: "Fin d'engagement", type: "date" as const, value: form.date_fin_engagement, onChange: (v: string) => setForm(f => ({ ...f, date_fin_engagement: v })) },
    { id: "notes", label: "Notes", type: "textarea" as const, value: form.notes, onChange: (v: string) => setForm(f => ({ ...f, notes: v })) },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📋 Abonnements</h1>
        <p className="text-muted-foreground">Comparateur d&apos;abonnements maison</p>
      </div>

      <BandeauIA section="abonnements" />

      {/* Résumé financier */}
      {resume && (
        <div className="grid grid-cols-2 gap-3">
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-xs text-muted-foreground">Coût mensuel</p>
              <p className="text-lg font-bold">{resume.total_mensuel.toFixed(2)} €</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3 text-center">
              <p className="text-xs text-muted-foreground">Coût annuel</p>
              <p className="text-lg font-bold">{resume.total_annuel.toFixed(2)} €</p>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter</Button>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-16" />)}</div>
      ) : !abonnements?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground">
          <Receipt className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="font-medium">Aucun abonnement enregistré</p>
          <p className="text-xs mt-1">Ajoutez vos abonnements pour suivre vos coûts</p>
        </CardContent></Card>
      ) : (
        <div className="space-y-2">
          {abonnements.map((abo) => {
            const finEngagement = abo.date_fin_engagement ? new Date(abo.date_fin_engagement) : null;
            const soonExpiring = finEngagement && finEngagement.getTime() - Date.now() < 30 * 86400000 && finEngagement.getTime() > Date.now();
            return (
              <SwipeableItem
                key={abo.id}
                labelGauche="Supprimer"
                labelDroit="Modifier"
                onSwipeLeft={() => supprimerAvecUndo(abo)}
                onSwipeRight={() => ouvrirEdition(abo)}
              >
                <Card className={soonExpiring ? "border-amber-300" : ""}>
                  <CardContent className="py-3 flex items-center gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium">{abo.fournisseur}</p>
                        <Badge variant="secondary" className="text-[10px]">
                          {TYPES_ABONNEMENT.find(t => t.valeur === abo.type_abonnement)?.label ?? abo.type_abonnement}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {abo.prix_mensuel ? `${abo.prix_mensuel.toFixed(2)} €/mois` : "—"}
                        {finEngagement && ` · engagement jusqu'au ${finEngagement.toLocaleDateString("fr-FR")}`}
                      </p>
                      {abo.meilleur_prix_trouve && abo.prix_mensuel && abo.meilleur_prix_trouve < abo.prix_mensuel && (
                        <p className="text-xs text-green-600 flex items-center gap-1 mt-0.5">
                          <TrendingDown className="h-3 w-3" />
                          {abo.fournisseur_alternatif}: {abo.meilleur_prix_trouve.toFixed(2)} €/mois
                          (−{(abo.prix_mensuel - abo.meilleur_prix_trouve).toFixed(2)} €)
                        </p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(abo)}><Pencil className="h-3.5 w-3.5" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimerAvecUndo(abo)}><Trash2 className="h-3.5 w-3.5" /></Button>
                    </div>
                  </CardContent>
                </Card>
              </SwipeableItem>
            );
          })}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier l'abonnement" : "Ajouter un abonnement"}
        champs={CHAMPS}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

export default function PageAbonnements() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-40" /><Skeleton className="h-10 w-48" /><Skeleton className="h-64" /></div>}>
      <ContenuAbonnements />
    </Suspense>
  );
}
