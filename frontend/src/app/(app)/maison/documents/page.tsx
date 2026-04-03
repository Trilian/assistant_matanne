// ═══════════════════════════════════════════════════════════
// Documents — Diagnostics
// Page documents maison
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  FileText, ClipboardCheck, Plus, Trash2, Pencil, AlertTriangle, Home,
} from "lucide-react";
import {
  Card, CardContent,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { utiliserSuppressionAnnulable } from "@/crochets/utiliser-suppression-annulable";
import { SwipeableItem } from "@/composants/swipeable-item";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerDiagnostics, alertesDiagnostics, derniereEstimation, creerDiagnostic, modifierDiagnostic, supprimerDiagnostic,
} from "@/bibliotheque/api/maison";
import type { DiagnosticImmobilier } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";


// ─── Onglet Diagnostics ───────────────────────────────────────
function OngletDiagnostics() {
  const formsVide = { type_diagnostic: "", date_realisation: "", date_expiration: "", resultat: "", diagnostiqueur: "" };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<DiagnosticImmobilier>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (d) => setForm({ type_diagnostic: d.type_diagnostic, date_realisation: d.date_realisation ?? "", date_expiration: d.date_expiration ?? "", resultat: d.resultat ?? "", diagnostiqueur: d.diagnostiqueur ?? "" }),
    });

  const { data: diagnostics, isLoading } = utiliserRequete(["maison", "diagnostics"], () => listerDiagnostics());
  const { data: alertes } = utiliserRequete(["maison", "diagnostics", "alertes"], alertesDiagnostics);
  const { data: estimation } = utiliserRequete(["maison", "diagnostics", "estimation"], derniereEstimation);
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "diagnostics"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerDiagnostic(data as Omit<DiagnosticImmobilier, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Diagnostic ajouté"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<DiagnosticImmobilier> }) => modifierDiagnostic(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Diagnostic modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerDiagnostic, { onSuccess: () => { invalider(); toast.success("Diagnostic supprimé"); } });
  const { planifierSuppression } = utiliserSuppressionAnnulable();

  const supprimerAvecUndo = (d: DiagnosticImmobilier) => {
    planifierSuppression(`diagnostic-${d.id}`, {
      libelle: d.type_diagnostic,
      onConfirmer: () => supprimer(d.id),
      onErreur: () => toast.error("Erreur lors de la suppression"),
    });
  };

  const soumettre = () => {
    const payload = { type_diagnostic: form.type_diagnostic, date_realisation: form.date_realisation || undefined, date_expiration: form.date_expiration || undefined, resultat: form.resultat || undefined, diagnostiqueur: form.diagnostiqueur || undefined };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload as Record<string, unknown>);
  };

  const CHAMPS = [
    { id: "type_diagnostic", label: "Type de diagnostic", type: "text" as const, value: form.type_diagnostic, onChange: (v: string) => setForm(f => ({ ...f, type_diagnostic: v })), required: true },
    { id: "date_realisation", label: "Date de réalisation", type: "date" as const, value: form.date_realisation, onChange: (v: string) => setForm(f => ({ ...f, date_realisation: v })) },
    { id: "date_expiration", label: "Date d'expiration", type: "date" as const, value: form.date_expiration, onChange: (v: string) => setForm(f => ({ ...f, date_expiration: v })) },
    { id: "resultat", label: "Résultat", type: "text" as const, value: form.resultat, onChange: (v: string) => setForm(f => ({ ...f, resultat: v })) },
    { id: "diagnostiqueur", label: "Diagnostiqueur", type: "text" as const, value: form.diagnostiqueur, onChange: (v: string) => setForm(f => ({ ...f, diagnostiqueur: v })) },
  ];

  return (
    <div className="space-y-4">
      {estimation && (
        <Card>
          <CardContent className="py-3 flex items-center gap-3">
            <Home className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Dernière estimation</p>
              <p className="text-lg font-bold">{estimation.valeur_estimee?.toLocaleString("fr-FR")} €</p>
              {estimation.date && <p className="text-xs text-muted-foreground">{new Date(estimation.date).toLocaleDateString("fr-FR")}</p>}
            </div>
          </CardContent>
        </Card>
      )}

      {(alertes?.length ?? 0) > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 mb-1.5 flex items-center gap-1.5"><AlertTriangle className="h-4 w-4" />{alertes!.length} diagnostic(s) expirant bientôt</p>
            {alertes!.slice(0, 3).map((d: { id: number; type_diagnostic: string; date_expiration?: string }) => (
              <p key={d.id} className="text-xs text-muted-foreground">• {d.type_diagnostic}{d.date_expiration ? ` (exp. ${new Date(d.date_expiration).toLocaleDateString("fr-FR")})` : ""}</p>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter un diagnostic</Button>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
      ) : !diagnostics?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><ClipboardCheck className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucun diagnostic enregistré</CardContent></Card>
      ) : (
        <div className="space-y-2">
          {diagnostics.map((d: DiagnosticImmobilier) => {
            const expire = d.date_expiration && new Date(d.date_expiration) < new Date(Date.now() + 90 * 86400000);
            return (
              <SwipeableItem
                key={d.id}
                labelGauche="Supprimer"
                labelDroit="Modifier"
                onSwipeLeft={() => supprimerAvecUndo(d)}
                onSwipeRight={() => ouvrirEdition(d)}
              >
                <Card className={expire ? "border-amber-200" : ""}>
                  <CardContent className="py-3 flex items-center gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{d.type_diagnostic}</p>
                      <p className="text-xs text-muted-foreground">
                        {d.resultat ?? "—"}{d.date_expiration ? ` · exp. ${new Date(d.date_expiration).toLocaleDateString("fr-FR")}` : ""}
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(d)}><Pencil className="h-3.5 w-3.5" /></Button>
                      <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimerAvecUndo(d)}><Trash2 className="h-3.5 w-3.5" /></Button>
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
        titre={enEdition ? "Modifier le diagnostic" : "Ajouter un diagnostic"}
        champs={CHAMPS}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

// ─── Page principale ──────────────────────────────────────────
function ContenuDocuments() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tab = searchParams.get("tab") ?? "diagnostics";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📄 Documents</h1>
        <p className="text-muted-foreground">Diagnostics immobiliers</p>
      </div>

      <BandeauIA section="documents" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="diagnostics"><ClipboardCheck className="h-4 w-4 mr-1.5" />Diagnostics</TabsTrigger>
        </TabsList>
        <TabsContent value="diagnostics" className="mt-4"><OngletDiagnostics /></TabsContent>
      </Tabs>
    </div>
  );
}

export default function PageDocuments() {
  return (
    <Suspense fallback={<div className="space-y-4"><Skeleton className="h-8 w-40" /><Skeleton className="h-10 w-48" /><Skeleton className="h-64" /></div>}>
      <ContenuDocuments />
    </Suspense>
  );
}
