"use client";

import { Brain, Coins, Database, Gauge, Loader2, RefreshCw } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { lireMetriquesIAAdmin } from "@/bibliotheque/api/admin";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PageAdminIAMetrics() {
  const { data, isLoading, refetch } = utiliserRequete(["admin", "ia-metrics"], lireMetriquesIAAdmin);

  const tokens = Number((data?.api?.tokens_used as number | undefined) ?? 0);
  const appels = Number((data?.api?.calls as number | undefined) ?? (data?.api?.total_calls as number | undefined) ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Brain className="h-6 w-6" />
            Metriques IA
          </h1>
          <p className="text-muted-foreground">Consommation IA, cache semantique et estimation de cout.</p>
        </div>
        <Button variant="outline" onClick={() => void refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Rafraichir
        </Button>
      </div>

      {isLoading && <Loader2 className="h-5 w-5 animate-spin" />}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2"><Gauge className="h-4 w-4" />Appels IA</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{appels}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2"><Brain className="h-4 w-4" />Tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tokens}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2"><Coins className="h-4 w-4" />Cout estime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.cout_estime_eur ?? 0} EUR</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2"><Database className="h-4 w-4" />Prix/1k tokens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.cout_eur_1k_tokens ?? 0} EUR</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Details techniques</CardTitle>
          <CardDescription>Snapshot brut des metriques IA admin.</CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-[480px]">
            {JSON.stringify(data ?? {}, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
