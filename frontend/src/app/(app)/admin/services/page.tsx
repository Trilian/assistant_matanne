// ═══════════════════════════════════════════════════════════
// Page Admin — Services, Cache, Flags & Re-sync
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useState } from "react";
import {
  CheckCircle2,
  DatabaseZap,
  Flag,
  FlaskConical,
  Download,
  Loader2,
  Play,
  RefreshCw,
  Repeat,
  ServerCrash,
  Settings2,
  Upload,
  Trash2,
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
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Textarea } from "@/composants/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/composants/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { utiliserRequete } from "@/crochets/utiliser-api";
import {
  type FlowSimulationResponse,
  type LiveSnapshotResponse,
  type StatutBridgesResponse,
  type ServiceHealthResponse,
  exporterConfigAdmin,
  exporterDbJson,
  executerActionService,
  forcerResync,
  importerDbJson,
  importerConfigAdmin,
  lancerSeedDev,
  lireFeatureFlags,
  lireRuntimeConfig,
  listerActionsServices,
  listerResyncTargets,
  obtenirLiveSnapshotAdmin,
  obtenirDashboardAdmin,
  obtenirStatutBridges,
  obtenirSanteServices,
  obtenirStatsCache,
  purgerCache,
  sauvegarderFeatureFlags,
  sauvegarderRuntimeConfig,
  simulerFluxAdmin,
  testerConsoleIA,
  viderCache,
} from "@/bibliotheque/api/admin";

interface StatsCache {
  l1_hits?: number;
  l3_hits?: number;
  misses?: number;
  writes?: number;
  message?: string;
}

interface ServiceInfoAffichee {
  status?: string;
  note?: string;
}

export default function PageAdminServices() {
  const [tab, setTab] = useState("services");
  const [patternPurge, setPatternPurge] = useState("*");
  const [purgeant, setPurgeant] = useState(false);
  const [vidant, setVidant] = useState(false);
  const [resultatCache, setResultatCache] = useState<string | null>(null);

  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);
  const [resultatAction, setResultatAction] = useState<string | null>(null);

  const [flagsLocal, setFlagsLocal] = useState<Record<string, boolean>>({});
  const [flagsSaving, setFlagsSaving] = useState(false);
  const [flagsResultat, setFlagsResultat] = useState<string | null>(null);

  const [configText, setConfigText] = useState("{}");
  const [configSaving, setConfigSaving] = useState(false);
  const [configResultat, setConfigResultat] = useState<string | null>(null);
  const [importText, setImportText] = useState("");
  const [importLoading, setImportLoading] = useState(false);

  const [resyncLoadingId, setResyncLoadingId] = useState<string | null>(null);
  const [resultatResync, setResultatResync] = useState<string | null>(null);

  const [seedLoading, setSeedLoading] = useState(false);
  const [seedResultat, setSeedResultat] = useState<string | null>(null);
  const [simulationScenario, setSimulationScenario] = useState<"peremption_j2" | "document_expirant" | "echec_cron_job" | "rappel_courses" | "resume_hebdo">("peremption_j2");
  const [simulationMessage, setSimulationMessage] = useState("");
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [simulationResultat, setSimulationResultat] = useState<FlowSimulationResponse | null>(null);
  const [iaPrompt, setIaPrompt] = useState("");
  const [iaResponse, setIaResponse] = useState("");
  const [iaLoading, setIaLoading] = useState(false);
  const [dbImportText, setDbImportText] = useState("");
  const [dbLoading, setDbLoading] = useState(false);
  const [dbResultat, setDbResultat] = useState<string | null>(null);
  const [wsConnecte, setWsConnecte] = useState(false);
  const [wsEvents1h, setWsEvents1h] = useState<number | null>(null);

  const {
    data: sante,
    isLoading: chargementSante,
    refetch: actualiserSante,
  } = utiliserRequete(["admin", "services-health"], async (): Promise<ServiceHealthResponse> => {
    return obtenirSanteServices();
  });

  const servicesAffiches = (sante?.services ?? {}) as Record<string, ServiceInfoAffichee>;

  const {
    data: statsCache,
    isLoading: chargementStats,
    refetch: actualiserStats,
  } = utiliserRequete(["admin", "cache-stats"], async (): Promise<StatsCache> => {
    return obtenirStatsCache() as Promise<StatsCache>;
  });

  const { data: dashboard, refetch: actualiserDashboard } = utiliserRequete(
    ["admin", "dashboard"],
    obtenirDashboardAdmin,
  );

  const { data: actionsServices, refetch: actualiserActions } = utiliserRequete(
    ["admin", "service-actions"],
    listerActionsServices,
  );

  const { data: featureFlags, refetch: actualiserFlags } = utiliserRequete(
    ["admin", "feature-flags"],
    lireFeatureFlags,
  );

  const { data: runtimeConfig, refetch: actualiserConfig } = utiliserRequete(
    ["admin", "runtime-config"],
    lireRuntimeConfig,
  );

  const { data: resyncTargets, refetch: actualiserResync } = utiliserRequete(
    ["admin", "resync-targets"],
    listerResyncTargets,
  );

  const { data: liveSnapshot, refetch: actualiserLive } = utiliserRequete(
    ["admin", "live-snapshot"],
    (): Promise<LiveSnapshotResponse> => obtenirLiveSnapshotAdmin(),
    { refetchInterval: 15000 },
  );

  const {
    data: statutBridges,
    isLoading: chargementBridges,
    refetch: actualiserBridges,
  } = utiliserRequete(
    ["admin", "bridges-status"],
    (): Promise<StatutBridgesResponse> => obtenirStatutBridges({ inclure_smoke: false }),
    { refetchInterval: 30000 },
  );

  useEffect(() => {
    if (featureFlags?.flags) {
      setFlagsLocal(featureFlags.flags);
    }
  }, [featureFlags?.flags]);

  useEffect(() => {
    if (runtimeConfig?.values) {
      setConfigText(JSON.stringify(runtimeConfig.values, null, 2));
    }
  }, [runtimeConfig?.values]);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) return;

    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const wsUrl = `${base.replace("http", "ws")}/api/v1/ws/admin/metrics?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => setWsConnecte(true);
    ws.onclose = () => setWsConnecte(false);
    ws.onerror = () => setWsConnecte(false);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as { security?: { events_1h?: number } };
        if (typeof data.security?.events_1h === "number") {
          setWsEvents1h(data.security.events_1h);
        }
      } catch {
        // ignore payload non JSON
      }
    };

    return () => ws.close();
  }, []);

  const actualiserTout = () => {
    actualiserSante();
    actualiserStats();
    actualiserDashboard();
    actualiserActions();
    actualiserFlags();
    actualiserConfig();
    actualiserResync();
    actualiserLive();
    actualiserBridges();
  };

  const exporterConfig = async () => {
    const data = await exporterConfigAdmin();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `admin-config-${new Date().toISOString().slice(0, 10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
    setConfigResultat("OK: configuration exportée.");
  };

  const importerConfig = async () => {
    setImportLoading(true);
    setConfigResultat(null);
    try {
      const parsed = JSON.parse(importText) as {
        feature_flags?: Record<string, boolean>
        runtime_config?: Record<string, unknown>
      };
      await importerConfigAdmin({
        feature_flags: parsed.feature_flags,
        runtime_config: parsed.runtime_config,
        merge: true,
      });
      setConfigResultat("OK: configuration importée.");
      actualiserFlags();
      actualiserConfig();
      actualiserDashboard();
    } catch {
      setConfigResultat("JSON invalide ou import impossible.");
    } finally {
      setImportLoading(false);
    }
  };

  const purgeCache = async () => {
    setPurgeant(true);
    setResultatCache(null);
    try {
      const data = await purgerCache(patternPurge);
      setResultatCache(`OK: ${data.message ?? "Cache purgé."}`);
      actualiserStats();
      actualiserDashboard();
    } catch {
      setResultatCache("Erreur lors de la purge du cache.");
    } finally {
      setPurgeant(false);
    }
  };

  const clearCache = async () => {
    setVidant(true);
    setResultatCache(null);
    try {
      const data = await viderCache();
      setResultatCache(`OK: ${data.message ?? "Cache vidé."}`);
      actualiserStats();
      actualiserDashboard();
    } catch {
      setResultatCache("Erreur lors du vidage du cache.");
    } finally {
      setVidant(false);
    }
  };

  const lancerActionService = async (actionId: string, dryRun: boolean) => {
    setActionLoadingId(actionId + String(dryRun));
    setResultatAction(null);
    try {
      const data = await executerActionService(actionId, { dry_run: dryRun });
      setResultatAction(`OK: ${actionId} (${String(data.status)})`);
      actualiserDashboard();
    } catch {
      setResultatAction(`Erreur exécution: ${actionId}`);
    } finally {
      setActionLoadingId(null);
    }
  };

  const saveFlags = async () => {
    setFlagsSaving(true);
    setFlagsResultat(null);
    try {
      await sauvegarderFeatureFlags(flagsLocal);
      setFlagsResultat("OK: feature flags sauvegardés.");
      actualiserFlags();
      actualiserDashboard();
    } catch {
      setFlagsResultat("Erreur de sauvegarde des feature flags.");
    } finally {
      setFlagsSaving(false);
    }
  };

  const saveRuntimeConfig = async () => {
    setConfigSaving(true);
    setConfigResultat(null);
    try {
      const parsed = JSON.parse(configText) as Record<string, unknown>;
      await sauvegarderRuntimeConfig(parsed);
      setConfigResultat("OK: configuration runtime sauvegardée.");
      actualiserConfig();
    } catch {
      setConfigResultat("JSON invalide ou erreur de sauvegarde.");
    } finally {
      setConfigSaving(false);
    }
  };

  const lancerResync = async (targetId: string, dryRun: boolean) => {
    setResyncLoadingId(targetId + String(dryRun));
    setResultatResync(null);
    try {
      const data = await forcerResync(targetId, dryRun);
      setResultatResync(`OK: ${targetId} (${String(data.status ?? "ok")})`);
      actualiserDashboard();
    } catch {
      setResultatResync(`Erreur re-sync ${targetId}.`);
    } finally {
      setResyncLoadingId(null);
    }
  };

  const lancerSeed = async (dryRun: boolean) => {
    setSeedLoading(true);
    setSeedResultat(null);
    try {
      const data = await lancerSeedDev("recettes_standard", dryRun);
      setSeedResultat(`OK: ${String(data.message ?? "Seed terminé")}`);
    } catch {
      setSeedResultat("Erreur seed (autorisé uniquement en dev/test). ");
    } finally {
      setSeedLoading(false);
    }
  };

  const lancerSimulation = async () => {
    setSimulationLoading(true);
    try {
      const data = await simulerFluxAdmin({
        scenario: simulationScenario,
        message: simulationMessage || undefined,
        dry_run: true,
      });
      setSimulationResultat(data);
    } catch {
      setSimulationResultat(null);
    } finally {
      setSimulationLoading(false);
    }
  };

  const executerConsoleIA = async () => {
    if (!iaPrompt.trim()) {
      setIaResponse("Le prompt est vide.");
      return;
    }
    setIaLoading(true);
    try {
      const data = await testerConsoleIA({ prompt: iaPrompt, utiliser_cache: false });
      setIaResponse(data.response ?? "(réponse vide)");
    } catch {
      setIaResponse("Erreur lors de l'appel IA.");
    } finally {
      setIaLoading(false);
    }
  };

  const exporterBackupDb = async () => {
    setDbLoading(true);
    setDbResultat(null);
    try {
      const data = await exporterDbJson();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `db-backup-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
      setDbResultat(`OK: export ${data.total_tables} table(s).`);
    } catch {
      setDbResultat("Erreur export DB.");
    } finally {
      setDbLoading(false);
    }
  };

  const importerBackupDb = async () => {
    setDbLoading(true);
    setDbResultat(null);
    try {
      const parsed = JSON.parse(dbImportText) as { tables: Record<string, Array<Record<string, unknown>>> };
      if (!parsed.tables || typeof parsed.tables !== "object") {
        throw new Error("invalid");
      }
      const data = await importerDbJson(parsed.tables, false);
      setDbResultat(`OK: import ${data.imported_tables} table(s).`);
    } catch {
      setDbResultat("JSON invalide ou import impossible (dev/test uniquement).");
    } finally {
      setDbLoading(false);
    }
  };

  const badgeStatut = (statut: string) => {
    if (statut === "healthy" || statut === "ok" || statut === "operationnel") {
      return <Badge variant="default"><CheckCircle2 className="mr-1 h-3 w-3" />Sain</Badge>;
    }
    if (statut === "degraded" || statut === "degrade") {
      return <Badge variant="secondary">Dégradé</Badge>;
    }
    return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />{statut}</Badge>;
  };

  const aiRequests = Number((liveSnapshot?.api.ai as Record<string, unknown> | undefined)?.requests_total ?? 0);
  const aiTokens = Number((liveSnapshot?.api.ai as Record<string, unknown> | undefined)?.tokens_used ?? 0);
  const aiCost = Number((liveSnapshot?.api.ai as Record<string, unknown> | undefined)?.estimated_cost_eur ?? 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <ServerCrash className="h-6 w-6" />
            Services & Cache
          </h1>
          <p className="text-muted-foreground">
            Cockpit admin: santé services, actions manuelles, flags et re-sync.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={actualiserTout} aria-label="Actualiser">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {dashboard && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Jobs actifs</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{dashboard.jobs.actifs}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Services sains</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{dashboard.services.healthy}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Sécurité (24h)</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{dashboard.security.events_24h}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Feature flags</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold">{Object.keys(dashboard.feature_flags ?? {}).length}</span></CardContent>
          </Card>
        </div>
      )}

      <Tabs value={tab} onValueChange={setTab} defaultValue="services">
        <TabsList className="grid w-full grid-cols-9 max-w-6xl">
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="cache">Cache</TabsTrigger>
          <TabsTrigger value="actions">Actions</TabsTrigger>
          <TabsTrigger value="flags">Flags</TabsTrigger>
          <TabsTrigger value="config">Config</TabsTrigger>
          <TabsTrigger value="resync">Re-sync</TabsTrigger>
          <TabsTrigger value="ia">Console IA</TabsTrigger>
          <TabsTrigger value="backup">Backup DB</TabsTrigger>
          <TabsTrigger value="simulateur">Simulateur</TabsTrigger>
        </TabsList>

        <TabsContent value="services" className="mt-4 space-y-4">
          {liveSnapshot && (
            <div className="grid gap-4 md:grid-cols-5">
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Requêtes API</CardTitle></CardHeader>
                <CardContent><span className="text-2xl font-bold">{liveSnapshot.api.requests_total}</span></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Latence moyenne</CardTitle></CardHeader>
                <CardContent><span className="text-2xl font-bold">{liveSnapshot.api.latency.avg_ms.toFixed(1)} ms</span></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">P95 max</CardTitle></CardHeader>
                <CardContent><span className="text-2xl font-bold">{liveSnapshot.api.latency.p95_ms.toFixed(1)} ms</span></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Sécurité 1h</CardTitle></CardHeader>
                <CardContent>
                  <span className="text-2xl font-bold">{wsEvents1h ?? liveSnapshot.security.events_1h}</span>
                  <p className="text-xs text-muted-foreground mt-1">{wsConnecte ? "Live WS" : "Polling"}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Coût IA estimé</CardTitle></CardHeader>
                <CardContent>
                  <span className="text-2xl font-bold">{aiCost.toFixed(3)} €</span>
                  <p className="text-xs text-muted-foreground mt-1">{aiRequests} appels • {aiTokens} tokens</p>
                </CardContent>
              </Card>
            </div>
          )}

          {sante && (
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Statut global</CardTitle></CardHeader>
                <CardContent>{badgeStatut(sante.global_status)}</CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Enregistrés</CardTitle></CardHeader>
                <CardContent><span className="text-2xl font-bold">{sante.total_services}</span></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Instanciés</CardTitle></CardHeader>
                <CardContent><span className="text-2xl font-bold">{sante.instantiated}</span></CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Sains</CardTitle></CardHeader>
                <CardContent><span className="text-2xl font-bold text-green-600">{sante.healthy}</span></CardContent>
              </Card>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Bridges inter-modules</CardTitle>
              <CardDescription>
                {chargementBridges
                  ? "Chargement..."
                  : statutBridges
                    ? `Mode ${statutBridges.resume.mode_verification} • ${statutBridges.resume.total_actions} action(s)`
                    : "-"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {statutBridges?.resume && (
                <div className="grid gap-4 md:grid-cols-4">
                  <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Statut global</CardTitle></CardHeader>
                    <CardContent>{badgeStatut(statutBridges.statut_global)}</CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Opérationnelles</CardTitle></CardHeader>
                    <CardContent><span className="text-2xl font-bold text-green-600">{statutBridges.resume.operationnelles}</span></CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Indisponibles</CardTitle></CardHeader>
                    <CardContent><span className="text-2xl font-bold">{statutBridges.resume.indisponibles}</span></CardContent>
                  </Card>
                  <Card>
                    <CardHeader className="pb-2"><CardTitle className="text-sm">Taux opérationnel</CardTitle></CardHeader>
                    <CardContent><span className="text-2xl font-bold">{statutBridges.resume.taux_operationnel_pct.toFixed(2)}%</span></CardContent>
                  </Card>
                </div>
              )}

              {statutBridges?.items?.length ? (
                <div className="overflow-x-auto rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Action</TableHead>
                        <TableHead>Bridge</TableHead>
                        <TableHead>Vérification</TableHead>
                        <TableHead>Statut</TableHead>
                        <TableHead>Latence</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {statutBridges.items.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>
                            <p className="font-mono text-xs">{item.id}</p>
                            <p className="text-xs text-muted-foreground">{item.intitule}</p>
                          </TableCell>
                          <TableCell className="font-mono text-xs">{item.bridge}</TableCell>
                          <TableCell>{item.verification}</TableCell>
                          <TableCell>{badgeStatut(item.statut)}</TableCell>
                          <TableCell>{item.latence_ms.toFixed(2)} ms</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                !chargementBridges && (
                  <p className="text-sm text-muted-foreground">Aucun statut bridge inter-modules disponible.</p>
                )
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Détail des services</CardTitle>
              <CardDescription>
                {chargementSante ? "Chargement..." : sante ? `${Object.keys(sante.services).length} service(s) instancié(s)` : "-"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {chargementSante ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  Chargement...
                </div>
              ) : sante && Object.keys(sante.services).length > 0 ? (
                <div className="overflow-x-auto rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Service</TableHead>
                        <TableHead>Statut</TableHead>
                        <TableHead>Note</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {Object.entries(servicesAffiches).map(([nom, info]) => (
                        <TableRow key={nom}>
                          <TableCell className="font-mono text-xs">{nom}</TableCell>
                          <TableCell>{badgeStatut(info.status ?? "unknown")}</TableCell>
                          <TableCell className="text-xs text-muted-foreground">{info.note ?? "-"}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-center py-8 text-muted-foreground text-sm">Aucun service instancié.</p>
              )}
            </CardContent>
          </Card>

          {liveSnapshot && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Zap className="h-4 w-4" />Snapshot live</CardTitle>
                <CardDescription>Mise à jour automatique toutes les 15 secondes.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-sm font-medium mb-2">Top endpoints</p>
                  <div className="space-y-2">
                    {liveSnapshot.api.top_endpoints.map((item) => (
                      <div key={item.endpoint} className="flex items-center justify-between text-sm border rounded-md px-3 py-2">
                        <span className="font-mono text-xs">{item.endpoint}</span>
                        <span>{item.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium mb-2">Jobs 24h</p>
                  <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-48">{JSON.stringify(liveSnapshot.jobs.last_24h, null, 2)}</pre>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="cache" className="mt-4 space-y-4">
          {!chargementStats && statsCache && !statsCache.message && (
            <div className="grid gap-4 md:grid-cols-4">
              {[
                { label: "Hits L1", val: statsCache.l1_hits },
                { label: "Hits L3", val: statsCache.l3_hits },
                { label: "Misses", val: statsCache.misses },
                { label: "Ecritures", val: statsCache.writes },
              ].map(({ label, val }) => (
                <Card key={label}>
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">{label}</CardTitle></CardHeader>
                  <CardContent><span className="text-2xl font-bold">{val ?? 0}</span></CardContent>
                </Card>
              ))}
            </div>
          )}

          {statsCache && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2"><DatabaseZap className="h-4 w-4" />Statistiques brutes</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-48">{JSON.stringify(statsCache, null, 2)}</pre>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Trash2 className="h-4 w-4" />Purger le cache</CardTitle>
              <CardDescription>Invalider des clés de cache par pattern.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 max-w-md">
              <div className="space-y-1">
                <Label htmlFor="pattern-purge">Pattern</Label>
                <Input id="pattern-purge" value={patternPurge} onChange={(e) => setPatternPurge(e.target.value)} />
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={purgeCache} disabled={purgeant}>
                  {purgeant ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
                  Purger
                </Button>
                <Button variant="destructive" onClick={clearCache} disabled={vidant}>
                  {vidant ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Vider tout
                </Button>
              </div>
              {resultatCache && <p className="text-sm text-muted-foreground">{resultatCache}</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="actions" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Play className="h-4 w-4" />Actions de services</CardTitle>
              <CardDescription>Exécution manuelle des actions whitelistées.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {!actionsServices?.items?.length ? (
                <p className="text-sm text-muted-foreground">Aucune action disponible.</p>
              ) : (
                actionsServices.items.map((action) => (
                  <div key={action.id} className="rounded-md border p-3 flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="text-sm font-medium">{action.id}</p>
                      <p className="text-xs text-muted-foreground">{action.description}</p>
                    </div>
                    <div className="flex gap-2">
                      {action.dry_run && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => lancerActionService(action.id, true)}
                          disabled={actionLoadingId !== null}
                        >
                          {actionLoadingId === action.id + "true" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Dry-run"}
                        </Button>
                      )}
                      <Button
                        size="sm"
                        onClick={() => lancerActionService(action.id, false)}
                        disabled={actionLoadingId !== null}
                      >
                        {actionLoadingId === action.id + "false" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Exécuter"}
                      </Button>
                    </div>
                  </div>
                ))
              )}
              {resultatAction && <p className="text-sm text-muted-foreground">{resultatAction}</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="flags" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Flag className="h-4 w-4" />Feature flags</CardTitle>
              <CardDescription>Activer/désactiver des fonctionnalités runtime.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.keys(flagsLocal).length === 0 ? (
                <p className="text-sm text-muted-foreground">Aucun flag disponible.</p>
              ) : (
                Object.entries(flagsLocal).map(([flag, enabled]) => (
                  <label key={flag} className="flex items-center justify-between gap-2 rounded-md border p-3 cursor-pointer">
                    <span className="font-mono text-xs">{flag}</span>
                    <input
                      type="checkbox"
                      checked={enabled}
                      onChange={(e) => setFlagsLocal((prev) => ({ ...prev, [flag]: e.target.checked }))}
                    />
                  </label>
                ))
              )}
              <Button onClick={saveFlags} disabled={flagsSaving}>
                {flagsSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Flag className="mr-2 h-4 w-4" />}
                Sauvegarder les flags
              </Button>
              {flagsResultat && <p className="text-sm text-muted-foreground">{flagsResultat}</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="config" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Settings2 className="h-4 w-4" />Configuration runtime</CardTitle>
              <CardDescription>Édition JSON des paramètres runtime admin.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea value={configText} onChange={(e) => setConfigText(e.target.value)} rows={12} className="font-mono text-xs" />
              <div className="flex flex-wrap gap-2">
                <Button onClick={saveRuntimeConfig} disabled={configSaving}>
                  {configSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Settings2 className="mr-2 h-4 w-4" />}
                  Sauvegarder la configuration
                </Button>
                <Button variant="outline" onClick={exporterConfig}>
                  <Download className="mr-2 h-4 w-4" />
                  Exporter
                </Button>
              </div>
              <Textarea
                value={importText}
                onChange={(e) => setImportText(e.target.value)}
                rows={8}
                className="font-mono text-xs"
                placeholder='Collez ici un export JSON admin à réimporter'
              />
              <Button variant="outline" onClick={importerConfig} disabled={importLoading}>
                {importLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
                Importer la configuration
              </Button>
              {configResultat && <p className="text-sm text-muted-foreground">{configResultat}</p>}
              {runtimeConfig?.readonly && (
                <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-48">{JSON.stringify(runtimeConfig.readonly, null, 2)}</pre>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resync" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Repeat className="h-4 w-4" />Re-sync externes</CardTitle>
              <CardDescription>Forcer les synchronisations Garmin / Google / OpenFoodFacts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {!resyncTargets?.items?.length ? (
                <p className="text-sm text-muted-foreground">Aucune cible disponible.</p>
              ) : (
                resyncTargets.items.map((target) => (
                  <div key={target.id} className="rounded-md border p-3 flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <p className="text-sm font-medium">{target.id}</p>
                      <p className="text-xs text-muted-foreground">{target.description}</p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => lancerResync(target.id, true)}
                        disabled={resyncLoadingId !== null}
                      >
                        {resyncLoadingId === target.id + "true" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Dry-run"}
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => lancerResync(target.id, false)}
                        disabled={resyncLoadingId !== null}
                      >
                        {resyncLoadingId === target.id + "false" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Lancer"}
                      </Button>
                    </div>
                  </div>
                ))
              )}
              {resultatResync && <p className="text-sm text-muted-foreground">{resultatResync}</p>}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><FlaskConical className="h-4 w-4" />Seed data dev</CardTitle>
              <CardDescription>Injection de recettes standard en environnement de dev/test.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => lancerSeed(true)} disabled={seedLoading}>
                  {seedLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Simuler seed
                </Button>
                <Button onClick={() => lancerSeed(false)} disabled={seedLoading}>
                  {seedLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Exécuter seed
                </Button>
              </div>
              {seedResultat && <p className="text-sm text-muted-foreground">{seedResultat}</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ia" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Zap className="h-4 w-4" />Console IA admin</CardTitle>
              <CardDescription>Tester un prompt et afficher la réponse brute.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Textarea
                rows={6}
                value={iaPrompt}
                onChange={(e) => setIaPrompt(e.target.value)}
                placeholder="Écrire un prompt de test..."
              />
              <Button onClick={executerConsoleIA} disabled={iaLoading}>
                {iaLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                Exécuter le prompt
              </Button>
              <Textarea rows={10} value={iaResponse} readOnly className="font-mono text-xs" />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="backup" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Download className="h-4 w-4" />Export / Import DB JSON</CardTitle>
              <CardDescription>Backup complet JSON et restauration (dev/test).</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex gap-2">
                <Button variant="outline" onClick={exporterBackupDb} disabled={dbLoading}>
                  {dbLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
                  Exporter DB JSON
                </Button>
              </div>
              <Textarea
                rows={10}
                value={dbImportText}
                onChange={(e) => setDbImportText(e.target.value)}
                className="font-mono text-xs"
                placeholder='Coller un backup JSON (format: {"tables": {...}})'
              />
              <Button onClick={importerBackupDb} disabled={dbLoading}>
                {dbLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
                Importer DB JSON
              </Button>
              {dbResultat && <p className="text-sm text-muted-foreground">{dbResultat}</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="simulateur" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><FlaskConical className="h-4 w-4" />Simulateur de flux</CardTitle>
              <CardDescription>Prévisualisez un scénario admin/inter-modules sans effet de bord.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1">
                <Label htmlFor="scenario-simulateur">Scénario</Label>
                <select
                  id="scenario-simulateur"
                  aria-label="Scénario de simulation"
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={simulationScenario}
                  onChange={(e) => setSimulationScenario(e.target.value as typeof simulationScenario)}
                >
                  <option value="peremption_j2">Péremption J-2</option>
                  <option value="document_expirant">Document expirant</option>
                  <option value="echec_cron_job">Échec job cron</option>
                  <option value="rappel_courses">Rappel courses</option>
                  <option value="resume_hebdo">Résumé hebdo</option>
                </select>
              </div>
              <div className="space-y-1">
                <Label htmlFor="message-simulateur">Message personnalisé</Label>
                <Textarea
                  id="message-simulateur"
                  rows={4}
                  value={simulationMessage}
                  onChange={(e) => setSimulationMessage(e.target.value)}
                  placeholder="Optionnel: surcharge du message simulé"
                />
              </div>
              <Button onClick={lancerSimulation} disabled={simulationLoading}>
                {simulationLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                Lancer la simulation
              </Button>
              {simulationResultat && (
                <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-96">{JSON.stringify(simulationResultat, null, 2)}</pre>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
