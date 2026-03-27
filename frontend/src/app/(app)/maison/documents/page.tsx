// ═══════════════════════════════════════════════════════════
// Documents — Contrats · Diagnostics (fusionnés en tabs)
// Phase 2B
// ═══════════════════════════════════════════════════════════

"use client";

import { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  FileText, ClipboardCheck, Plus, Trash2, Pencil, AlertTriangle, Home,
} from "lucide-react";
import {
  Card, CardContent, CardHeader, CardTitle, CardDescription,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import { utiliserRequete, utiliserMutation } from "@/crochets/utiliser-api";
import { useQueryClient } from "@tanstack/react-query";
import { utiliserDialogCrud } from "@/crochets/utiliser-crud";
import { DialogueFormulaire } from "@/composants/dialogue-formulaire";
import {
  listerContrats, alertesContrats, resumeFinancierContrats, creerContrat, modifierContrat, supprimerContrat,
  listerDiagnostics, alertesDiagnostics, listerEstimations, derniereEstimation, creerDiagnostic, modifierDiagnostic, supprimerDiagnostic,
} from "@/bibliotheque/api/maison";
import type { Contrat, DiagnosticImmobilier } from "@/types/maison";
import { toast } from "sonner";
import { BandeauIA } from "@/composants/maison/bandeau-ia";

// ─── Onglet Contrats ──────────────────────────────────────────
function OngletContrats() {
  const formsVide = { nom: "", type_contrat: "", fournisseur: "", montant_mensuel: "", date_debut: "", date_fin: "", statut: "actif" };
  const [form, setForm] = useState(formsVide);
  const queryClient = useQueryClient();

  const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
    utiliserDialogCrud<Contrat>({
      onOuvrirCreation: () => setForm(formsVide),
      onOuvrirEdition: (c) => setForm({ nom: c.nom, type_contrat: c.type_contrat ?? "", fournisseur: c.fournisseur ?? "", montant_mensuel: c.montant_mensuel != null ? String(c.montant_mensuel) : "", date_debut: c.date_debut ?? "", date_fin: c.date_fin ?? "", statut: c.statut ?? "actif" }),
    });

  const { data: contrats, isLoading } = utiliserRequete(["maison", "contrats"], () => listerContrats());
  const { data: alertes } = utiliserRequete(["maison", "contrats", "alertes"], () => alertesContrats(60));
  const { data: resume } = utiliserRequete(["maison", "contrats", "resume"], resumeFinancierContrats);
  const invalider = () => queryClient.invalidateQueries({ queryKey: ["maison", "contrats"] });

  const { mutate: creer, isPending: enCreation } = utiliserMutation(
    (data: Record<string, unknown>) => creerContrat(data as Omit<Contrat, "id">),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Contrat créé"); } }
  );
  const { mutate: modifier, isPending: enModif } = utiliserMutation(
    ({ id, data }: { id: number; data: Partial<Contrat> }) => modifierContrat(id, data),
    { onSuccess: () => { invalider(); fermerDialog(); toast.success("Contrat modifié"); } }
  );
  const { mutate: supprimer } = utiliserMutation(supprimerContrat, { onSuccess: () => { invalider(); toast.success("Contrat supprimé"); } });

  const soumettre = () => {
    const payload = { nom: form.nom, type_contrat: form.type_contrat || undefined, fournisseur: form.fournisseur || undefined, montant_mensuel: form.montant_mensuel ? Number(form.montant_mensuel) : undefined, date_debut: form.date_debut || undefined, date_fin: form.date_fin || undefined, statut: form.statut };
    if (enEdition) modifier({ id: enEdition.id, data: payload });
    else creer(payload as Record<string, unknown>);
  };

  const CHAMPS = [
    { id: "nom", label: "Nom du contrat", type: "text" as const, value: form.nom, onChange: (v: string) => setForm(f => ({ ...f, nom: v })), required: true },
    { id: "type_contrat", label: "Type", type: "text" as const, value: form.type_contrat, onChange: (v: string) => setForm(f => ({ ...f, type_contrat: v })) },
    { id: "fournisseur", label: "Fournisseur", type: "text" as const, value: form.fournisseur, onChange: (v: string) => setForm(f => ({ ...f, fournisseur: v })) },
    { id: "montant_mensuel", label: "Montant mensuel (€)", type: "number" as const, value: form.montant_mensuel, onChange: (v: string) => setForm(f => ({ ...f, montant_mensuel: v })) },
    { id: "date_debut", label: "Date début", type: "date" as const, value: form.date_debut, onChange: (v: string) => setForm(f => ({ ...f, date_debut: v })) },
    { id: "date_fin", label: "Date fin", type: "date" as const, value: form.date_fin, onChange: (v: string) => setForm(f => ({ ...f, date_fin: v })) },
  ];

  return (
    <div className="space-y-4">
      {resume && (
        <div className="grid grid-cols-2 gap-3">
          <Card><CardContent className="py-3"><p className="text-xs text-muted-foreground">Mensuel total</p><p className="text-xl font-bold">{(resume.mensuel_total ?? 0).toFixed(2)} €</p></CardContent></Card>
          <Card><CardContent className="py-3"><p className="text-xs text-muted-foreground">Annuel total</p><p className="text-xl font-bold">{(resume.annuel_total ?? 0).toFixed(2)} €</p></CardContent></Card>
        </div>
      )}

      {alertes?.length > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 mb-1.5 flex items-center gap-1.5"><AlertTriangle className="h-4 w-4" />{alertes.length} contrat(s) expirant bientôt</p>
            {alertes.slice(0, 3).map((c: { id: number; nom: string; date_fin?: string }) => (
              <p key={c.id} className="text-xs text-muted-foreground">• {c.nom}{c.date_fin ? ` (fin ${new Date(c.date_fin).toLocaleDateString("fr-FR")})` : ""}</p>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="flex justify-end">
        <Button size="sm" onClick={ouvrirCreation}><Plus className="mr-2 h-4 w-4" />Ajouter un contrat</Button>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <Skeleton key={i} className="h-14" />)}</div>
      ) : !contrats?.length ? (
        <Card><CardContent className="py-10 text-center text-muted-foreground"><FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />Aucun contrat enregistré</CardContent></Card>
      ) : (
        <div className="space-y-2">
          {contrats.map((c: Contrat) => (
            <Card key={c.id}>
              <CardContent className="py-3 flex items-center gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">{c.nom}</p>
                    {c.statut && <Badge variant={c.statut === "actif" ? "secondary" : "outline"} className="text-xs">{c.statut}</Badge>}
                  </div>
                  <p className="text-xs text-muted-foreground">{c.fournisseur ?? "—"}{c.montant_mensuel != null ? ` · ${c.montant_mensuel.toFixed(2)} €/mois` : ""}</p>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(c)}><Pencil className="h-3.5 w-3.5" /></Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimer(c.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <DialogueFormulaire
        ouvert={dialogOuvert}
        onChangerOuvert={setDialogOuvert}
        titre={enEdition ? "Modifier le contrat" : "Ajouter un contrat"}
        champs={CHAMPS}
        onSoumettre={soumettre}
        enChargement={enCreation || enModif}
      />
    </div>
  );
}

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
              {estimation.date_estimation && <p className="text-xs text-muted-foreground">{new Date(estimation.date_estimation).toLocaleDateString("fr-FR")}</p>}
            </div>
          </CardContent>
        </Card>
      )}

      {alertes?.length > 0 && (
        <Card className="border-amber-300">
          <CardContent className="py-3">
            <p className="text-sm font-medium text-amber-700 mb-1.5 flex items-center gap-1.5"><AlertTriangle className="h-4 w-4" />{alertes.length} diagnostic(s) expirant bientôt</p>
            {alertes.slice(0, 3).map((d: { id: number; type_diagnostic: string; date_expiration?: string }) => (
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
              <Card key={d.id} className={expire ? "border-amber-200" : ""}>
                <CardContent className="py-3 flex items-center gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{d.type_diagnostic}</p>
                    <p className="text-xs text-muted-foreground">
                      {d.resultat ?? "—"}{d.date_expiration ? ` · exp. ${new Date(d.date_expiration).toLocaleDateString("fr-FR")}` : ""}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => ouvrirEdition(d)}><Pencil className="h-3.5 w-3.5" /></Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 hover:text-destructive" onClick={() => supprimer(d.id)}><Trash2 className="h-3.5 w-3.5" /></Button>
                  </div>
                </CardContent>
              </Card>
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
  const tab = searchParams.get("tab") ?? "contrats";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📄 Documents</h1>
        <p className="text-muted-foreground">Contrats et diagnostics immobiliers</p>
      </div>

      <BandeauIA section="documents" />

      <Tabs value={tab} onValueChange={(val) => router.replace(`?tab=${val}`)}>
        <TabsList>
          <TabsTrigger value="contrats"><FileText className="h-4 w-4 mr-1.5" />Contrats</TabsTrigger>
          <TabsTrigger value="diagnostics"><ClipboardCheck className="h-4 w-4 mr-1.5" />Diagnostics</TabsTrigger>
        </TabsList>
        <TabsContent value="contrats" className="mt-4"><OngletContrats /></TabsContent>
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
