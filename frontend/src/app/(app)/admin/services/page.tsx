// ═══════════════════════════════════════════════════════════
// Page Admin — Services & Cache
// ═══════════════════════════════════════════════════════════

"use client";

import { RefreshCw, ServerCrash, CheckCircle2, XCircle, Loader2, Trash2, DatabaseZap } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
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
import { clientApi } from "@/bibliotheque/api/client";
import { useState } from "react";

interface ServiceSante {
  status: string;
  note?: string;
}

interface SanteGlobale {
  global_status: string;
  total_services: number;
  instantiated: number;
  healthy: number;
  erreurs: string[];
  services: Record<string, ServiceSante>;
  metriques?: {
    total_enregistres: number;
    total_instancies: number;
    services: Record<string, { instancié: boolean; accès: number; tags: string[] }>;
  };
}

interface StatsCache {
  l1_hits?: number;
  l2_hits?: number;
  l3_hits?: number;
  misses?: number;
  writes?: number;
  evictions?: number;
  l1?: Record<string, unknown>;
  l3_size?: number;
  message?: string;
}

export default function PageAdminServices() {
  const [patternPurge, setPatternPurge] = useState("*");
  const [purgeant, setPurgeant] = useState(false);
  const [vidant, setVidant] = useState(false);
  const [resultatCache, setResultatCache] = useState<string | null>(null);

  const {
    data: sante,
    isLoading: chargementSante,
    refetch: actualiserSante,
  } = utiliserRequete(["admin", "services-health"], async (): Promise<SanteGlobale> => {
    const { data } = await clientApi.get("/admin/services/health");
    return data;
  });

  const {
    data: statsCache,
    isLoading: chargementStats,
    refetch: actualiserStats,
  } = utiliserRequete(["admin", "cache-stats"], async (): Promise<StatsCache> => {
    const { data } = await clientApi.get("/admin/cache/stats");
    return data;
  });

  const purgerCache = async () => {
    setPurgeant(true);
    setResultatCache(null);
    try {
      const { data } = await clientApi.post("/admin/cache/purge", { pattern: patternPurge });
      setResultatCache(`✅ ${data.message ?? "Cache purgé."}`);
      actualiserStats();
    } catch {
      setResultatCache("❌ Erreur lors de la purge.");
    } finally {
      setPurgeant(false);
    }
  };

  const viderCache = async () => {
    setVidant(true);
    setResultatCache(null);
    try {
      const { data } = await clientApi.post("/admin/cache/clear");
      setResultatCache(`✅ ${data.message ?? "Cache vidé."}`);
      actualiserStats();
    } catch {
      setResultatCache("❌ Erreur lors du vidage.");
    } finally {
      setVidant(false);
    }
  };

  const statutBadge = (statut: string) => {
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
            Services &amp; Cache
          </h1>
          <p className="text-muted-foreground">
            État de santé des services et gestion du cache applicatif
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => { actualiserSante(); actualiserStats(); }}
          aria-label="Actualiser"
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <Tabs defaultValue="services">
        <TabsList className="grid w-full grid-cols-2 max-w-sm">
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="cache">Cache</TabsTrigger>
        </TabsList>

        {/* ── Onglet Services ─────────────────────────────────── */}
        <TabsContent value="services" className="mt-4 space-y-4">
          {/* Résumé global */}
          {sante && (
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Statut global</CardTitle>
                </CardHeader>
                <CardContent>{statutBadge(sante.global_status)}</CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Enregistrés</CardTitle>
                </CardHeader>
                <CardContent>
                  <span className="text-2xl font-bold">{sante.total_services}</span>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Instanciés</CardTitle>
                </CardHeader>
                <CardContent>
                  <span className="text-2xl font-bold">{sante.instantiated}</span>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Sains</CardTitle>
                </CardHeader>
                <CardContent>
                  <span className="text-2xl font-bold text-green-600">{sante.healthy}</span>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Erreurs */}
          {sante?.erreurs && sante.erreurs.length > 0 && (
            <Card className="border-destructive">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-destructive">Erreurs détectées</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm text-destructive list-disc pl-4 space-y-1">
                  {sante.erreurs.map((e, i) => <li key={i}>{e}</li>)}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Tableau services */}
          <Card>
            <CardHeader>
              <CardTitle>Détail des services</CardTitle>
              <CardDescription>
                {chargementSante ? "Chargement…" : sante
                  ? `${Object.keys(sante.services).length} service(s) instancié(s)`
                  : "—"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {chargementSante ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  Chargement…
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
                      {Object.entries(sante.services).map(([nom, info]) => (
                        <TableRow key={nom}>
                          <TableCell className="font-mono text-xs">{nom}</TableCell>
                          <TableCell>{statutBadge(info.status)}</TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {info.note ?? "—"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-center py-8 text-muted-foreground text-sm">
                  Aucun service instancié.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Onglet Cache ────────────────────────────────────── */}
        <TabsContent value="cache" className="mt-4 space-y-4">
          {/* Métriques cache */}
          {statsCache && !statsCache.message && (
            <div className="grid gap-4 md:grid-cols-4">
              {[
                { label: "Hits L1", val: statsCache.l1_hits },
                { label: "Hits L3", val: statsCache.l3_hits },
                { label: "Misses", val: statsCache.misses },
                { label: "Écritures", val: statsCache.writes },
              ].map(({ label, val }) => (
                <Card key={label}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{label}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <span className="text-2xl font-bold">{val ?? 0}</span>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {statsCache && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <DatabaseZap className="h-4 w-4" />Statistiques brutes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-48">
                  {JSON.stringify(statsCache, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Purge par pattern */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trash2 className="h-4 w-4" />Purger par pattern
              </CardTitle>
              <CardDescription>
                Invalide les clés correspondant au pattern (ex : <code>recettes_*</code>).
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 max-w-md">
              <div className="space-y-1">
                <Label htmlFor="pattern-purge">Pattern</Label>
                <Input
                  id="pattern-purge"
                  placeholder="*"
                  value={patternPurge}
                  onChange={(e) => setPatternPurge(e.target.value)}
                />
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={purgerCache} disabled={purgeant}>
                  {purgeant ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
                  Purger
                </Button>
                <Button variant="destructive" onClick={viderCache} disabled={vidant}>
                  {vidant ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Vider tout (L1 + L3)
                </Button>
              </div>
              {resultatCache && (
                <p className="text-sm text-muted-foreground">{resultatCache}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
