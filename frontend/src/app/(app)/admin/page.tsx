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
  ServerCrash,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import {
  Bell,
  Bot,
  Flag,
  Inbox,
  DatabaseZap,
  MessageSquare,
  Play,
  Sparkles,
  Trash2,
  Clock,
  Send,
  Loader2,
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/composants/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete, utiliserInvalidation } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { obtenirStatutBridges } from "@/bibliotheque/api/admin";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { GrapheReseauModules } from "@/composants/admin/graphe-reseau-modules";
import type { ObjetDonnees } from "@/types/commun";

interface LogAudit {
  id: number | null;
  timestamp: string;
  action: string;
  source: string;
  utilisateur_id: string | null;
  entite_type: string;
  entite_id: string | number | null;
  details: ObjetDonnees;
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

interface UtilisateurAdmin {
  id: string;
  email: string;
  nom: string | null;
  role: string;
  actif: boolean;
  cree_le: string | null;
}

interface SecurityLog {
  id: number;
  created_at: string;
  event_type: string;
  user_id: string | null;
  ip: string | null;
  user_agent: string | null;
  source: string;
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
  // Notifications test
  const [canalNotif, setCanalNotif] = useState<"ntfy" | "push" | "email" | "telegram">("ntfy");
  const [messageNotif, setMessageNotif] = useState("");
  const [emailNotif, setEmailNotif] = useState("");
  const [envoyant, setEnvoyant] = useState(false);
  const [resultatNotif, setResultatNotif] = useState<string | null>(null);
  // Cache purge
  const [patternCache, setPatternCache] = useState("*");
  const [purgeant, setPurgeant] = useState(false);
  const [resultatCache, setResultatCache] = useState<string | null>(null);

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

  const { data: utilisateurs } = utiliserRequete(
    ["admin", "users"],
    async (): Promise<UtilisateurAdmin[]> => {
      const { data } = await clientApi.get("/admin/users?par_page=100");
      return data;
    }
  );

  const { data: statsCache } = utiliserRequete(
    ["admin", "cache-stats"],
    async () => {
      const { data } = await clientApi.get("/admin/cache/stats");
      return data;
    }
  );

  const { data: securityLogs } = utiliserRequete(
    ["admin", "security-logs"],
    async (): Promise<{ items: SecurityLog[] }> => {
      const { data } = await clientApi.get("/admin/security-logs?par_page=8");
      return data;
    }
  );

  const { data: bridgesStatus } = utiliserRequete(
    ["admin", "bridges-status", "presence-only"],
    async () => obtenirStatutBridges({ inclure_smoke: false }),
    { refetchInterval: 30000 }
  );

  const envoyerNotifTest = async () => {
    setEnvoyant(true);
    setResultatNotif(null);
    try {
      const body: Record<string, string> = {
        canal: canalNotif,
        message: messageNotif || "Test Matanne",
        titre: "Test depuis l'admin",
      };
      if (canalNotif === "email" && emailNotif) body.email = emailNotif;
      await clientApi.post("/admin/notifications/test", body);
      setResultatNotif("✅ Notification envoyée avec succès.");
    } catch {
      setResultatNotif("❌ Erreur lors de l'envoi.");
    } finally {
      setEnvoyant(false);
    }
  };

  const purgerCache = async () => {
    setPurgeant(true);
    setResultatCache(null);
    try {
      const { data } = await clientApi.post("/admin/cache/purge", {
        pattern: patternCache,
      });
      setResultatCache(`✅ ${data.message ?? "Cache purgé."}`);
    } catch {
      setResultatCache("❌ Erreur lors de la purge du cache.");
    } finally {
      setPurgeant(false);
    }
  };

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

  const exporterPDF = async () => {
    const params = new URLSearchParams();
    if (filtreAction) params.append("action", filtreAction);
    if (filtreEntite) params.append("entite_type", filtreEntite);
    const response = await clientApi.get(`/admin/audit-export/pdf?${params}`, { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit-logs-${format(new Date(), "yyyy-MM-dd")}.pdf`;
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
            Administration
          </h1>
          <p className="text-muted-foreground">
            Surveillance, jobs, notifications et gestion des utilisateurs
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
        </div>
      </div>

      {/* Accès rapides vers les pages dédiées */}
      <div className="grid gap-3 md:grid-cols-5 xl:grid-cols-7">
        {[
          { href: "/admin/jobs", icon: Clock, label: "Jobs planifiés", desc: "Trigger + logs" },
          { href: "/admin/services", icon: ServerCrash, label: "Services & Cache", desc: "Health + stats" },
          { href: "/admin/notifications", icon: Bell, label: "Notifications", desc: "Test canaux" },
          { href: "/admin/utilisateurs", icon: Users, label: "Utilisateurs", desc: "Comptes + désactiver" },
          { href: "/admin/sql-views", icon: Layers, label: "Vues SQL", desc: "Lecture analytics" },
          { href: "/admin/events", icon: Activity, label: "Event Bus", desc: "Historique + trigger" },
          { href: "/admin/automations", icon: Bot, label: "Automations", desc: "Exécutions manuelles" },
          { href: "/admin/ia-metrics", icon: Sparkles, label: "Métriques IA", desc: "Coût + tokens" },
          { href: "/admin/notifications-queue", icon: Inbox, label: "Queue Notifs", desc: "Flush digest" },
          { href: "/admin/feature-flags", icon: Flag, label: "Feature Flags", desc: "Runtime toggles" },
          { href: "/admin/cache", icon: DatabaseZap, label: "Cache dédié", desc: "Purge sélective" },
          { href: "/admin/telegram-test", icon: MessageSquare, label: "Telegram test", desc: "Chat cible" },
          { href: "/admin/console", icon: Play, label: "Console rapide", desc: "Commandes admin" },
          { href: "/admin/scheduler", icon: Clock, label: "Scheduler visuel", desc: "Timeline CRON" },
          { href: "/admin/logs", icon: Activity, label: "Logs live", desc: "WebSocket temps réel" },
        ].map(({ href, icon: Icon, label, desc }) => (
          <Link key={href} href={href}>
            <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
              <CardContent className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <Icon className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-xs text-muted-foreground">{desc}</p>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {bridgesStatus?.resume && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Bridges inter-modules</CardTitle>
            <CardDescription>
              {bridgesStatus.resume.mode_verification} · {bridgesStatus.resume.total_actions} action(s)
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap items-center gap-2">
            <Badge variant={bridgesStatus.statut_global === "operationnel" ? "default" : "secondary"}>
              {bridgesStatus.statut_global === "operationnel" ? "Opérationnel" : "Dégradé"}
            </Badge>
            <Badge variant="outline">{bridgesStatus.resume.operationnelles} OK</Badge>
            <Badge variant="outline">{bridgesStatus.resume.indisponibles} KO</Badge>
            <Badge variant="outline">{bridgesStatus.resume.taux_operationnel_pct.toFixed(2)}%</Badge>
            <Button asChild variant="outline" size="sm" className="ml-auto">
              <Link href="/admin/services">Voir le détail</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {bridgesStatus?.items?.length ? (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Graphe réseau des modules</CardTitle>
            <CardDescription>Visualisation D3.js force-directed des 21 modules et leurs 21+ inter-connections.</CardDescription>
          </CardHeader>
          <CardContent>
            <GrapheReseauModules width={1000} height={600} />
          </CardContent>
        </Card>
      ) : null}

      <Tabs defaultValue="audit">
        <TabsList className="grid w-full grid-cols-5 max-w-2xl">
          <TabsTrigger value="audit">
            <Activity className="mr-1.5 h-4 w-4 hidden sm:inline" />Audit
          </TabsTrigger>
          <TabsTrigger value="jobs">
            <Clock className="mr-1.5 h-4 w-4 hidden sm:inline" />Jobs
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="mr-1.5 h-4 w-4 hidden sm:inline" />Notifs
          </TabsTrigger>
          <TabsTrigger value="cache">
            <DatabaseZap className="mr-1.5 h-4 w-4 hidden sm:inline" />Cache
          </TabsTrigger>
          <TabsTrigger value="users">
            <Users className="mr-1.5 h-4 w-4 hidden sm:inline" />Utilisateurs
          </TabsTrigger>
        </TabsList>

        {/* ── Onglet Audit ───────────────────────────────────────── */}
        <TabsContent value="audit" className="space-y-4 mt-4">
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

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Événements sécurité récents</CardTitle>
              <CardDescription>Auth, actions admin et événements sensibles.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {!securityLogs?.items?.length ? (
                <p className="text-sm text-muted-foreground">Aucun événement de sécurité récent.</p>
              ) : (
                securityLogs.items.map((evt) => (
                  <div key={evt.id} className="rounded-md border p-2.5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-medium truncate">{evt.event_type}</p>
                      <Badge variant="outline" className="shrink-0">{evt.source || "unknown"}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {format(new Date(evt.created_at), "dd/MM/yyyy HH:mm", { locale: fr })}
                      {evt.user_id ? ` · user ${evt.user_id}` : ""}
                      {evt.ip ? ` · ip ${evt.ip}` : ""}
                    </p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {stats && (actionsData.length > 0 || entitesData.length > 0) && (
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader><CardTitle className="text-sm">Top actions</CardTitle></CardHeader>
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
                <CardHeader><CardTitle className="text-sm">Actions par entité</CardTitle></CardHeader>
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

          <Card>
            <CardHeader>
              <CardTitle>Journal d&apos;audit</CardTitle>
              <CardDescription>
                {logs ? `${logs.total} entrées trouvées` : "Chargement…"}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-3 flex-wrap items-end">
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
                <Button variant="outline" size="sm" onClick={exporterCSV}>
                  <Download className="mr-2 h-4 w-4" />Export CSV
                </Button>
                <Button variant="outline" size="sm" onClick={exporterPDF}>
                  <Download className="mr-2 h-4 w-4" />Export PDF
                </Button>
              </div>

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
                  {logs.pages_totales > 1 && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">
                        Page {logs.page} / {logs.pages_totales}
                      </span>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" disabled={page === 1}
                          onClick={() => setPage((p) => p - 1)}>Précédent</Button>
                        <Button variant="outline" size="sm" disabled={page >= logs.pages_totales}
                          onClick={() => setPage((p) => p + 1)}>Suivant</Button>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <p className="py-4 text-center text-muted-foreground text-sm">Aucun log trouvé</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Onglet Jobs ─────────────────────────────────────────── */}
        <TabsContent value="jobs" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />Jobs planifiés
              </CardTitle>
              <CardDescription>
                Gérez les tâches automatiques depuis{" "}
                <Link href="/admin/jobs" className="underline text-primary">
                  la page dédiée
                </Link>{" "}
                pour plus de détails.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild>
                <Link href="/admin/jobs">
                  <Play className="mr-2 h-4 w-4" />Gérer les jobs
                </Link>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Onglet Notifications ────────────────────────────────── */}
        <TabsContent value="notifications" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />Notification de test
              </CardTitle>
              <CardDescription>
                Envoyez une notification de test.{" "}
                <Link href="/admin/notifications" className="underline text-primary">
                  Page dédiée avec historique →
                </Link>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 max-w-md">
              <div className="space-y-1">
                <Label htmlFor="canal-notif">Canal</Label>
                <Select
                  value={canalNotif}
                  onValueChange={(v) => setCanalNotif(v as typeof canalNotif)}
                >
                  <SelectTrigger id="canal-notif">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ntfy">ntfy.sh</SelectItem>
                    <SelectItem value="push">Web Push</SelectItem>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="telegram">Telegram</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {canalNotif === "email" && (
                <div className="space-y-1">
                  <Label htmlFor="email-notif">Adresse email destinataire</Label>
                  <Input
                    id="email-notif"
                    type="email"
                    placeholder="email@exemple.fr"
                    value={emailNotif}
                    onChange={(e) => setEmailNotif(e.target.value)}
                  />
                </div>
              )}

              <div className="space-y-1">
                <Label htmlFor="message-notif">Message</Label>
                <Input
                  id="message-notif"
                  placeholder="Message de test..."
                  value={messageNotif}
                  onChange={(e) => setMessageNotif(e.target.value)}
                />
              </div>

              <Button onClick={envoyerNotifTest} disabled={envoyant}>
                {envoyant ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Send className="mr-2 h-4 w-4" />
                )}
                Envoyer le test
              </Button>

              {resultatNotif && (
                <p className="text-sm text-muted-foreground">{resultatNotif}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Onglet Cache ────────────────────────────────────────── */}
        <TabsContent value="cache" className="mt-4 space-y-4">
          {/* Stats */}
          {statsCache && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Statistiques cache</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-muted rounded p-3 overflow-auto max-h-40">
                  {JSON.stringify(statsCache, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Purge */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trash2 className="h-5 w-5" />Purger le cache
              </CardTitle>
              <CardDescription>
                Invalide les entrées correspondant au pattern (ex : <code>recettes_*</code>, <code>*</code> pour tout purger).
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 max-w-md">
              <div className="space-y-1">
                <Label htmlFor="pattern-cache">Pattern</Label>
                <Input
                  id="pattern-cache"
                  placeholder="*"
                  value={patternCache}
                  onChange={(e) => setPatternCache(e.target.value)}
                />
              </div>
              <Button variant="destructive" onClick={purgerCache} disabled={purgeant}>
                {purgeant ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="mr-2 h-4 w-4" />
                )}
                Purger
              </Button>
              {resultatCache && (
                <p className="text-sm text-muted-foreground">{resultatCache}</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Onglet Utilisateurs ─────────────────────────────────── */}
        <TabsContent value="users" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />Comptes utilisateurs
              </CardTitle>
              <CardDescription>
                {utilisateurs ? `${utilisateurs.length} compte(s)` : "Chargement…"}{" "}
                —{" "}
                <Link href="/admin/utilisateurs" className="underline text-primary">
                  Gérer les comptes →
                </Link>
              </CardDescription>
            </CardHeader>
            <CardContent>
              {utilisateurs && utilisateurs.length > 0 ? (
                <div className="overflow-x-auto rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Email</TableHead>
                        <TableHead>Nom</TableHead>
                        <TableHead>Rôle</TableHead>
                        <TableHead>Statut</TableHead>
                        <TableHead>Créé le</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {utilisateurs.map((u) => (
                        <TableRow key={u.id}>
                          <TableCell className="text-sm">{u.email}</TableCell>
                          <TableCell className="text-sm">{u.nom ?? "—"}</TableCell>
                          <TableCell>
                            <Badge variant={u.role === "admin" ? "default" : "secondary"}>
                              {u.role}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={u.actif ? "default" : "outline"}>
                              {u.actif ? "Actif" : "Inactif"}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {u.cree_le
                              ? format(new Date(u.cree_le), "dd/MM/yyyy", { locale: fr })
                              : "—"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-center py-8 text-muted-foreground text-sm">
                  Aucun utilisateur trouvé.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
