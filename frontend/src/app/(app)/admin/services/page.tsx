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
  Loader2,
  Play,
  RefreshCw,
  Repeat,
  ServerCrash,
  Settings2,
  Trash2,
  XCircle,
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
  type ServiceHealthResponse,
  executerActionService,
  forcerResync,
  lancerSeedDev,
  lireFeatureFlags,
  lireRuntimeConfig,
  listerActionsServices,
  listerResyncTargets,
  obtenirDashboardAdmin,
  obtenirSanteServices,
  obtenirStatsCache,
  purgerCache,
  sauvegarderFeatureFlags,
  sauvegarderRuntimeConfig,
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

  const [resyncLoadingId, setResyncLoadingId] = useState<string | null>(null);
  const [resultatResync, setResultatResync] = useState<string | null>(null);

  const [seedLoading, setSeedLoading] = useState(false);
  const [seedResultat, setSeedResultat] = useState<string | null>(null);

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

  const actualiserTout = () => {
    actualiserSante();
    actualiserStats();
    actualiserDashboard();
    actualiserActions();
    actualiserFlags();
    actualiserConfig();
    actualiserResync();
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

  const badgeStatut = (statut: string) => {
    if (statut === "healthy" || statut === "ok") {
      return <Badge variant="default"><CheckCircle2 className="mr-1 h-3 w-3" />Sain</Badge>;
    }
    if (statut === "degraded") {
      return <Badge variant="secondary">Dégradé</Badge>;
    }
    return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />{statut}</Badge>;
  };

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
        <TabsList className="grid w-full grid-cols-6 max-w-5xl">
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="cache">Cache</TabsTrigger>
          <TabsTrigger value="actions">Actions</TabsTrigger>
          <TabsTrigger value="flags">Flags</TabsTrigger>
          <TabsTrigger value="config">Config</TabsTrigger>
          <TabsTrigger value="resync">Re-sync</TabsTrigger>
        </TabsList>

        <TabsContent value="services" className="mt-4 space-y-4">
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
              <Button onClick={saveRuntimeConfig} disabled={configSaving}>
                {configSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Settings2 className="mr-2 h-4 w-4" />}
                Sauvegarder la configuration
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
      </Tabs>
    </div>
  );
}
