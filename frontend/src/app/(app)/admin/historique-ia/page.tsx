"use client";

import Link from "next/link";
import { useMemo } from "react";
import { ArrowLeft, Brain, Coins, History, RefreshCw, Sparkles } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Skeleton } from "@/composants/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerAuditLogs, lireMetriquesIAAdmin } from "@/bibliotheque/api/admin";

interface EntreeAuditIA {
  id: number | null;
  timestamp: string;
  action: string;
  source: string;
  entite_type: string;
  details?: Record<string, unknown> | null;
}

function formaterDate(dateIso?: string | null) {
  if (!dateIso) return "-";
  return new Date(dateIso).toLocaleString("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatterDetails(details?: Record<string, unknown> | null) {
  if (!details || typeof details !== "object") return "-";
  const texte = JSON.stringify(details);
  return texte.length > 120 ? `${texte.slice(0, 117)}...` : texte;
}

export default function PageHistoriqueIA() {
  const {
    data: metrics,
    isLoading: chargementMetriques,
    refetch,
  } = utiliserRequete(["admin", "ia-metrics"], lireMetriquesIAAdmin);

  const { data: auditLogs, isLoading: chargementLogs } = utiliserRequete(
    ["admin", "historique-ia", "audit-logs"],
    async () => listerAuditLogs({ page: 1, par_page: 100 })
  );

  const historiqueIA = useMemo(() => {
    const items = (auditLogs?.items ?? []) as EntreeAuditIA[];

    return items
      .filter((item) => {
        const bloc = [
          item.action,
          item.source,
          item.entite_type,
          JSON.stringify(item.details ?? {}),
        ]
          .join(" ")
          .toLowerCase();

        return bloc.includes("ia") || bloc.includes("mistral") || bloc.includes("ai");
      })
      .slice(0, 25);
  }, [auditLogs?.items]);

  const appels = Number((metrics?.api?.calls as number | undefined) ?? (metrics?.api?.total_calls as number | undefined) ?? 0);
  const tokens = Number((metrics?.api?.tokens_used as number | undefined) ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="outline">Historique</Badge>
            <Badge>Admin</Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <History className="h-6 w-6" />
            Historique IA
          </h1>
          <p className="text-muted-foreground">
            Vue rapide des usages IA, métriques et événements d&apos;audit récents.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button asChild variant="outline">
            <Link href="/admin">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Retour admin
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/admin/ia-metrics">
              <Sparkles className="mr-2 h-4 w-4" />
              Métriques IA
            </Link>
          </Button>
          <Button variant="outline" onClick={() => void refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Rafraîchir
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Appels IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chargementMetriques ? <Skeleton className="h-8 w-20" /> : <div className="text-2xl font-bold">{appels}</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Tokens consommés
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chargementMetriques ? <Skeleton className="h-8 w-24" /> : <div className="text-2xl font-bold">{tokens}</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Coins className="h-4 w-4" />
              Coût estimé
            </CardTitle>
          </CardHeader>
          <CardContent>
            {chargementMetriques ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <div className="text-2xl font-bold">{metrics?.cout_estime_eur ?? 0} EUR</div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Événements IA récents</CardTitle>
          <CardDescription>
            Audit filtré côté client sur les actions liées à l&apos;IA, aux prompts et aux métriques.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {chargementLogs ? (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, index) => (
                <Skeleton key={index} className="h-10 w-full" />
              ))}
            </div>
          ) : historiqueIA.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Aucun événement IA récent n&apos;a été trouvé dans les 100 dernières entrées d&apos;audit.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Horodatage</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead>Entité</TableHead>
                  <TableHead>Détails</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {historiqueIA.map((item) => (
                  <TableRow key={`${item.id ?? "log"}-${item.timestamp}-${item.action}`}>
                    <TableCell className="whitespace-nowrap text-sm">{formaterDate(item.timestamp)}</TableCell>
                    <TableCell className="font-medium">{item.action}</TableCell>
                    <TableCell>{item.source}</TableCell>
                    <TableCell>{item.entite_type}</TableCell>
                    <TableCell className="max-w-[420px] truncate text-xs text-muted-foreground">
                      {formatterDetails(item.details)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
