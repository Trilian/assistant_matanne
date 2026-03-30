"use client";

import { FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerContrats, alertesContrats, resumeFinancierContrats } from "@/bibliotheque/api/maison";

interface ResumeContrats {
  total_mensuel?: number;
  total_annuel?: number;
}

export default function PageContratsMaison() {
  const { data: contrats = [], isLoading } = utiliserRequete(["maison", "contrats"], () => listerContrats());
  const { data: alertes = [] } = utiliserRequete(["maison", "contrats", "alertes"], () => alertesContrats(90));
  const { data: resume } = utiliserRequete<ResumeContrats>(["maison", "contrats", "resume"], resumeFinancierContrats);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">📄 Contrats</h1>
        <p className="text-muted-foreground">Suivi des contrats, échéances et coûts récurrents</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{contrats.length}</p><p className="text-xs text-muted-foreground">Contrats</p></CardContent></Card>
        <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold text-amber-500">{alertes.length}</p><p className="text-xs text-muted-foreground">Alertes 90j</p></CardContent></Card>
        <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{Number(resume?.total_mensuel ?? 0).toFixed(0)} €</p><p className="text-xs text-muted-foreground">Mensuel</p></CardContent></Card>
        <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{Number(resume?.total_annuel ?? 0).toFixed(0)} €</p><p className="text-xs text-muted-foreground">Annuel</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Contrats actifs</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14" />)}</div>
          ) : contrats.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucun contrat enregistré.</p>
          ) : (
            contrats.map((contrat) => (
              <div key={contrat.id} className="rounded-md border p-3 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium truncate">{contrat.nom}</p>
                  <p className="text-xs text-muted-foreground truncate">{contrat.fournisseur ?? "Fournisseur non précisé"}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={contrat.statut === "actif" ? "default" : "secondary"}>{contrat.statut ?? "inconnu"}</Badge>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
