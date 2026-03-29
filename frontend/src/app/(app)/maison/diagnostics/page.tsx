"use client";

import { ClipboardCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerDiagnostics, alertesDiagnostics } from "@/bibliotheque/api/maison";

export default function PageDiagnosticsMaison() {
  const { data: diagnostics = [], isLoading } = utiliserRequete(["maison", "diagnostics"], listerDiagnostics);
  const { data: alertes = [] } = utiliserRequete(["maison", "diagnostics", "alertes"], () => alertesDiagnostics(120));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🧪 Diagnostics</h1>
        <p className="text-muted-foreground">DPE, amiante, plomb et validité des diagnostics immobiliers</p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{diagnostics.length}</p><p className="text-xs text-muted-foreground">Diagnostics</p></CardContent></Card>
        <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold text-amber-500">{alertes.length}</p><p className="text-xs text-muted-foreground">Expirent bientôt</p></CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">État des diagnostics</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14" />)}</div>
          ) : diagnostics.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucun diagnostic enregistré.</p>
          ) : (
            diagnostics.map((diag) => (
              <div key={diag.id} className="rounded-md border p-3 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium truncate">{diag.type_diagnostic ?? "Diagnostic"}</p>
                  <p className="text-xs text-muted-foreground truncate">
                    {diag.date_realisation ? new Date(diag.date_realisation).toLocaleDateString("fr-FR") : "Date inconnue"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={diag.date_expiration ? "secondary" : "default"}>
                    {diag.date_expiration ? `Expire ${new Date(diag.date_expiration).toLocaleDateString("fr-FR")}` : "Sans expiration"}
                  </Badge>
                  <ClipboardCheck className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
