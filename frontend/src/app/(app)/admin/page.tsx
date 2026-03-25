// ═══════════════════════════════════════════════════════════
// Page Admin — Audit Logs
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import {
  Shield,
  Download,
  RefreshCw,
  Activity,
  Users,
  Layers,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Input } from "@/composants/ui/input";
import { Label } from "@/composants/ui/label";
import { Badge } from "@/composants/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import { utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

interface LogAudit {
  id: number | null;
  timestamp: string;
  action: string;
  source: string;
  utilisateur_id: string | null;
  entite_type: string;
  entite_id: string | number | null;
  details: Record<string, unknown>;
}

interface ReponseAuditLogs {
  items: LogAudit[];
  total: number;
  page: number;
  par_page: number;
  pages_totales: number;
}

interface StatsAudit {
  total_entrees: number;
  par_action: Record<string, number>;
  par_entite: Record<string, number>;
  par_source: Record<string, number>;
  souscrit_bus: boolean;
}

const COULEURS = [
  "#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed",
  "#0891b2", "#db2777", "#65a30d",
];

export default function PageAdmin() {
  const [filtreAction, setFiltreAction] = useState("");
  const [filtreEntite, setFiltreEntite] = useState("");
  const [page, setPage] = useState(1);
  const invalider = utiliserInvalidation();

  const { data: logs, isLoading } = utiliserRequete(
    ["admin", "audit-logs", String(page), filtreAction, filtreEntite],
    async (): Promise<ReponseAuditLogs> => {
      const params = new URLSearchParams({ page: String(page), par_page: "25" });
      if (filtreAction) params.append("action", filtreAction);
      if (filtreEntite) params.append("entite_type", filtreEntite);
      const { data } = await clientApi.get(`/admin/audit-logs?${params}`);
      return data;
    }
  );

  const { data: stats } = utiliserRequete(
    ["admin", "audit-stats"],
    async (): Promise<StatsAudit> => {
      const { data } = await clientApi.get("/admin/audit-stats");
      return data;
    }
  );

  const exporterCSV = async () => {
    const params = new URLSearchParams();
    if (filtreAction) params.append("action", filtreAction);
    if (filtreEntite) params.append("entite_type", filtreEntite);
    const response = await clientApi.get(`/admin/audit-export?${params}`, { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-logs-${format(new Date(), "yyyy-MM-dd")}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const actionsData = stats
    ? Object.entries(stats.par_action)
        .slice(0, 8)
        .map(([action, count]) => ({ action: action.split(".").pop() ?? action, count }))
    : [];

  const entitesData = stats
    ? Object.entries(stats.par_entite)
        .slice(0, 8)
        .map(([entite, count]) => ({ entite, count }))
    : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Administration — Audit Logs
          </h1>
          <p className="text-muted-foreground">
            Journal d&apos;activité et surveillance de l&apos;application
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => invalider(["admin"])}
            aria-label="Actualiser les logs"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={exporterCSV}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Métriques rapides */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total entrées</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_entrees.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                {stats.souscrit_bus ? "Bus connecté ✓" : "Bus non connecté"}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Types d&apos;actions</CardTitle>
              <Layers className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Object.keys(stats.par_action).length}</div>
              <p className="text-xs text-muted-foreground">actions distinctes</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Entités suivies</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Object.keys(stats.par_entite).length}</div>
              <p className="text-xs text-muted-foreground">types d&apos;entités</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Graphiques */}
      {stats && (actionsData.length > 0 || entitesData.length > 0) && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Top actions</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={actionsData} layout="vertical">
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="action" type="category" tick={{ fontSize: 10 }} width={80} />
                  <Tooltip />
                  <Bar dataKey="count">
                    {actionsData.map((_, i) => (
                      <Cell key={i} fill={COULEURS[i % COULEURS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Actions par entité</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={entitesData} layout="vertical">
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis dataKey="entite" type="category" tick={{ fontSize: 10 }} width={80} />
                  <Tooltip />
                  <Bar dataKey="count">
                    {entitesData.map((_, i) => (
                      <Cell key={i} fill={COULEURS[i % COULEURS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filtres + Table */}
      <Card>
        <CardHeader>
          <CardTitle>Journal d&apos;audit</CardTitle>
          <CardDescription>
            {logs ? `${logs.total} entrées trouvées` : "Chargement…"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Filtres */}
          <div className="flex gap-3 flex-wrap">
            <div className="space-y-1">
              <Label htmlFor="filtre-action" className="text-xs">Action</Label>
              <Input
                id="filtre-action"
                placeholder="recette.creee"
                value={filtreAction}
                onChange={(e) => { setFiltreAction(e.target.value); setPage(1); }}
                className="w-48 h-8 text-sm"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="filtre-entite" className="text-xs">Type d&apos;entité</Label>
              <Input
                id="filtre-entite"
                placeholder="recette"
                value={filtreEntite}
                onChange={(e) => { setFiltreEntite(e.target.value); setPage(1); }}
                className="w-40 h-8 text-sm"
              />
            </div>
          </div>

          {/* Table */}
          {isLoading ? (
            <p className="py-4 text-center text-muted-foreground text-sm">Chargement…</p>
          ) : logs && logs.items.length > 0 ? (
            <>
              <div className="overflow-x-auto rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-36">Timestamp</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead className="w-28">Entité</TableHead>
                      <TableHead className="w-20">ID</TableHead>
                      <TableHead>Source</TableHead>
                      <TableHead className="w-28">Utilisateur</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logs.items.map((log, i) => (
                      <TableRow key={log.id ?? i}>
                        <TableCell className="text-xs text-muted-foreground font-mono">
                          {format(new Date(log.timestamp), "dd/MM HH:mm:ss", { locale: fr })}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-xs font-mono">
                            {log.action}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs">{log.entite_type || "—"}</TableCell>
                        <TableCell className="text-xs font-mono">
                          {log.entite_id != null ? String(log.entite_id) : "—"}
                        </TableCell>
                        <TableCell className="text-xs text-muted-foreground">{log.source || "—"}</TableCell>
                        <TableCell className="text-xs font-mono">
                          {log.utilisateur_id ? log.utilisateur_id.slice(0, 8) + "…" : "—"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              {logs.pages_totales > 1 && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">
                    Page {logs.page} / {logs.pages_totales}
                  </span>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page === 1}
                      onClick={() => setPage((p) => p - 1)}
                    >
                      Précédent
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page >= logs.pages_totales}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Suivant
                    </Button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="py-4 text-center text-muted-foreground text-sm">
              Aucun log trouvé
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
