"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import {
  Activity,
  AlertTriangle,
  Brain,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  Gauge,
  HardDrive,
  Loader2,
  RefreshCw,
  Server,
  Shield,
  Wifi,
  XCircle,
  Zap,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import { Progress } from "@/composants/ui/progress";
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirSanteServices,
  obtenirStatsCache,
  lireMetriquesIAAdmin,
  obtenirLiveSnapshotAdmin,
  obtenirDashboardAdmin,
  type ServiceHealthResponse,
  type AiMetricsResponse,
  type LiveSnapshotResponse,
  type AdminDashboardResponse,
  type CacheStatsResponse,
} from "@/bibliotheque/api/admin";
import type { ObjetDonnees } from "@/types/commun";

const ResponsiveContainer = dynamic(
  () => import("recharts").then((m) => m.ResponsiveContainer),
  { ssr: false }
);
const BarChart = dynamic(
  () => import("recharts").then((m) => m.BarChart),
  { ssr: false }
);
const Bar = dynamic(
  () => import("recharts").then((m) => m.Bar),
  { ssr: false }
);
const XAxis = dynamic(
  () => import("recharts").then((m) => m.XAxis),
  { ssr: false }
);
const YAxis = dynamic(
  () => import("recharts").then((m) => m.YAxis),
  { ssr: false }
);
const Tooltip = dynamic(
  () => import("recharts").then((m) => m.Tooltip),
  { ssr: false }
);
const Cell = dynamic(
  () => import("recharts").then((m) => m.Cell),
  { ssr: false }
);

function formatUptime(seconds: number): string {
  const jours = Math.floor(seconds / 86400);
  const heures = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (jours > 0) return `${jours}j ${heures}h`;
  if (heures > 0) return `${heures}h ${minutes}m`;
  return `${minutes}m`;
}

function StatutBadge({ statut }: { statut: string }) {
  const estOk = statut === "healthy" || statut === "ok" || statut === "running";
  return (
    <Badge variant={estOk ? "default" : "destructive"} className={estOk ? "bg-green-600" : ""}>
      {estOk ? <CheckCircle2 className="mr-1 h-3 w-3" /> : <XCircle className="mr-1 h-3 w-3" />}
      {statut}
    </Badge>
  );
}

export default function PageMonitoring() {
  const [autoRefresh, setAutoRefresh] = useState(true);

  const { data: snapshot, isLoading: chargSnapshot, refetch: refetchSnapshot } = utiliserRequete(
    ["admin", "monitoring", "snapshot"],
    obtenirLiveSnapshotAdmin,
    { refetchInterval: autoRefresh ? 15000 : false }
  );

  const { data: sante, isLoading: chargSante, refetch: refetchSante } = utiliserRequete(
    ["admin", "monitoring", "sante"],
    obtenirSanteServices,
    { refetchInterval: autoRefresh ? 30000 : false }
  );

  const { data: iaMetrics, isLoading: chargIA, refetch: refetchIA } = utiliserRequete(
    ["admin", "monitoring", "ia"],
    lireMetriquesIAAdmin,
    { refetchInterval: autoRefresh ? 30000 : false }
  );

  const { data: cache, isLoading: chargCache } = utiliserRequete(
    ["admin", "monitoring", "cache"],
    obtenirStatsCache,
    { refetchInterval: autoRefresh ? 30000 : false }
  );

  const { data: dashboard } = utiliserRequete(
    ["admin", "monitoring", "dashboard"],
    obtenirDashboardAdmin,
    { refetchInterval: autoRefresh ? 60000 : false }
  );

  const rafraichirTout = () => {
    void refetchSnapshot();
    void refetchSante();
    void refetchIA();
  };

  const uptime = snapshot?.api?.uptime_seconds ?? 0;
  const requestsTotal = snapshot?.api?.requests_total ?? 0;
  const latencyAvg = snapshot?.api?.latency?.avg_ms ?? 0;
  const latencyP95 = snapshot?.api?.latency?.p95_ms ?? 0;
  const securityEvents = snapshot?.security?.events_1h ?? 0;
  const tokensIA = Number((iaMetrics?.api as ObjetDonnees)?.tokens_used ?? 0);
  const appelsIA = Number((iaMetrics?.api as ObjetDonnees)?.calls ?? (iaMetrics?.api as ObjetDonnees)?.total_calls ?? 0);
  const coutIA = iaMetrics?.cout_estime_eur ?? 0;

  const topEndpoints = snapshot?.api?.top_endpoints ?? [];
  const endpointsData = topEndpoints.slice(0, 8).map((ep: { endpoint: string; count: number }) => ({
    name: ep.endpoint.replace(/^\/api\/v1\//, "").slice(0, 20),
    count: ep.count,
  }));

  const servicesEntries = sante?.services
    ? Object.entries(sante.services as Record<string, ObjetDonnees>)
    : [];

  const jobsLast24h = snapshot?.jobs?.last_24h ?? {};
  const jobsData = Object.entries(jobsLast24h).map(([name, count]) => ({
    name: name.slice(0, 18),
    count: Number(count),
  }));

  const chargement = chargSnapshot || chargSante || chargIA;

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Monitoring
          </h1>
          <p className="text-muted-foreground">
            Vue d&apos;ensemble temps réel — style Grafana
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={autoRefresh ? "default" : "outline"}
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <Wifi className={`mr-2 h-4 w-4 ${autoRefresh ? "animate-pulse" : ""}`} />
            {autoRefresh ? "Live" : "Pause"}
          </Button>
          <Button variant="outline" size="sm" onClick={rafraichirTout}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Rafraîchir
          </Button>
        </div>
      </div>

      {chargement && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Chargement des métriques…
        </div>
      )}

      {/* KPI principales */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4 text-blue-500" />
              Uptime
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatUptime(uptime)}</div>
            <p className="text-xs text-muted-foreground">{requestsTotal.toLocaleString()} requêtes totales</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Gauge className="h-4 w-4 text-green-500" />
              Latence moyenne
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{latencyAvg.toFixed(0)} ms</div>
            <p className="text-xs text-muted-foreground">P95 : {latencyP95.toFixed(0)} ms</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Brain className="h-4 w-4 text-purple-500" />
              Usage IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{appelsIA} appels</div>
            <p className="text-xs text-muted-foreground">{tokensIA.toLocaleString()} tokens · {coutIA.toFixed(3)} €</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4 text-amber-500" />
              Sécurité
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{securityEvents}</div>
            <p className="text-xs text-muted-foreground">événements sécurité (1h)</p>
          </CardContent>
        </Card>
      </div>

      {/* Santé des services */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            Santé des services
          </CardTitle>
          <CardDescription>
            {sante?.healthy ?? 0}/{sante?.total_services ?? 0} services opérationnels
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Progress
              value={sante?.total_services ? ((sante.healthy ?? 0) / sante.total_services) * 100 : 0}
              className="h-2"
            />
          </div>
          {sante?.global_status && (
            <div className="mb-4">
              <StatutBadge statut={sante.global_status} />
            </div>
          )}
          {servicesEntries.length > 0 && (
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {servicesEntries.map(([nom, info]) => (
                <div
                  key={nom}
                  className="flex items-center justify-between rounded-md border px-3 py-2"
                >
                  <span className="text-sm truncate">{nom}</span>
                  <StatutBadge
                    statut={
                      typeof info === "object" && info !== null
                        ? String((info as Record<string, unknown>).status ?? "unknown")
                        : String(info)
                    }
                  />
                </div>
              ))}
            </div>
          )}
          {sante?.erreurs && sante.erreurs.length > 0 && (
            <div className="mt-4 space-y-1">
              {sante.erreurs.map((err, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-destructive">
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                  {err}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Graphiques */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Top endpoints */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Top endpoints (requêtes)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {endpointsData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={endpointsData} layout="vertical" margin={{ left: 10, right: 10 }}>
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {endpointsData.map((_: unknown, i: number) => (
                        <Cell key={i} fill={`hsl(${220 + i * 15}, 70%, 55%)`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucune donnée disponible</p>
            )}
          </CardContent>
        </Card>

        {/* Jobs dernières 24h */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              Jobs exécutés (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {jobsData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={jobsData} layout="vertical" margin={{ left: 10, right: 10 }}>
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {jobsData.map((_: unknown, i: number) => (
                        <Cell key={i} fill={`hsl(${140 + i * 20}, 60%, 50%)`} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucun job exécuté</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Métriques IA détaillées + Cache */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Détails IA
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Metrique label="Rate limit" valeur={formatObj(iaMetrics?.rate_limit)} />
              <Metrique label="Cache IA" valeur={formatObj(iaMetrics?.cache)} />
            </div>
            {iaMetrics?.monitoring && (
              <div className="rounded-md border bg-muted/30 p-3">
                <p className="mb-1 text-xs font-medium text-muted-foreground">Monitoring</p>
                <pre className="text-xs whitespace-pre-wrap overflow-auto max-h-32">
                  {JSON.stringify(iaMetrics.monitoring, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <HardDrive className="h-4 w-4" />
              Cache
            </CardTitle>
          </CardHeader>
          <CardContent>
            {cache ? (
              <div className="rounded-md border bg-muted/30 p-3">
                <pre className="text-xs whitespace-pre-wrap overflow-auto max-h-48">
                  {JSON.stringify(cache, null, 2)}
                </pre>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucune donnée cache</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Métriques système */}
      {dashboard && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Database className="h-4 w-4" />
              Vue d&apos;ensemble système
            </CardTitle>
            <CardDescription>
              Généré à {new Date(dashboard.generated_at).toLocaleString("fr-FR")}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-md border p-3 text-center">
                <p className="text-2xl font-bold">{dashboard.jobs?.total ?? 0}</p>
                <p className="text-xs text-muted-foreground">
                  Jobs ({dashboard.jobs?.actifs ?? 0} actifs)
                </p>
              </div>
              <div className="rounded-md border p-3 text-center">
                <p className="text-2xl font-bold">{dashboard.security?.events_24h ?? 0}</p>
                <p className="text-xs text-muted-foreground">Events sécurité (24h)</p>
              </div>
              <div className="rounded-md border p-3 text-center">
                <p className="text-2xl font-bold">
                  {Object.keys(dashboard.feature_flags ?? {}).length}
                </p>
                <p className="text-xs text-muted-foreground">Feature flags</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Metrique({ label, valeur }: { label: string; valeur: string }) {
  return (
    <div className="rounded-md border p-2">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium truncate">{valeur}</p>
    </div>
  );
}

function formatObj(obj: unknown): string {
  if (!obj) return "—";
  if (typeof obj === "string" || typeof obj === "number") return String(obj);
  const entries = Object.entries(obj as Record<string, unknown>);
  if (entries.length === 0) return "—";
  return entries
    .slice(0, 3)
    .map(([k, v]) => `${k}: ${v}`)
    .join(", ");
}
