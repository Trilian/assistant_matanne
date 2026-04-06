// ═══════════════════════════════════════════════════════════
// Page Admin — Jobs Cron
// ═══════════════════════════════════════════════════════════

"use client";

import { Fragment, useEffect, useState } from "react";
import { Play, RefreshCw, Clock, CheckCircle2, XCircle, Loader2, FileText } from "lucide-react";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/composants/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/composants/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { clientApi } from "@/bibliotheque/api/client";
import { format, parseISO } from "date-fns";
import { fr } from "date-fns/locale";
import { toast } from "sonner";
import {
  comparerDryRunVsRun,
  declencherJobAvecOptions,
  executerJobsDuMatin,
  executerTousLesJobs,
  listerHistoriqueJobs,
  listerJobs,
  mettreAJourScheduleJob,
  relancerJobDepuisHistorique,
  simulerJourneeJobs,
  type JobCompareResponse,
  type JobBatchResponse,
} from "@/bibliotheque/api/admin";

interface JobInfo {
  id: string;
  nom: string;
  schedule: string;
  prochain_run: string | null;
  dernier_run: string | null;
  statut: "actif" | "inactif";
}

interface JobLog {
  timestamp: string;
  status: "succes" | "erreur";
  message: string;
}

interface JobLogsResponse {
  job_id: string;
  nom: string;
  logs: JobLog[];
  total: number;
}

interface JobHistoryEntry {
  id: number;
  job_id: string;
  job_name: string;
  started_at: string | null;
  ended_at: string | null;
  duration_ms: number;
  status: string;
  error_message: string | null;
  output_logs: string | null;
  triggered_by_user_id: string | null;
  triggered_by_user_role: string | null;
}

interface JobHistoryResponse {
  items: JobHistoryEntry[];
  total: number;
  page: number;
  par_page: number;
  pages_totales: number;
}

interface LiveAdminLogEntry {
  type?: "log_entry";
  timestamp: string;
  level: string;
  module: string;
  message: string;
}

type RunStatus = "idle" | "running" | "success" | "error";

function obtenirTokenAdmin(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("access_token") ?? "";
}

function obtenirWsAdminBaseUrl(): string {
  if (typeof window === "undefined") return "";
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return apiUrl.replace(/^http/, "ws");
}

function formaterDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return format(parseISO(iso), "dd/MM/yyyy HH:mm", { locale: fr });
  } catch {
    return iso;
  }
}

export default function PageAdminJobs() {
  const [runStatuts, setRunStatuts] = useState<Record<string, RunStatus>>({});
  const [jobLogsOuverts, setJobLogsOuverts] = useState<Record<string, boolean>>({});
  const [jobLogs, setJobLogs] = useState<Record<string, JobLogsResponse>>({});
  const [chargementLogs, setChargementLogs] = useState<Record<string, boolean>>({});
  const [modeDryRun, setModeDryRun] = useState(false);
  const [modeForce, setModeForce] = useState(false);
  const [pageHistorique, setPageHistorique] = useState(1);
  const [filtreJobId, setFiltreJobId] = useState("");
  const [filtreStatus, setFiltreStatus] = useState("all");
  const [filtreDepuis, setFiltreDepuis] = useState("");
  const [filtreJusqua, setFiltreJusqua] = useState("");
  const [confirmJobId, setConfirmJobId] = useState<string | null>(null);
  const [paramsJson, setParamsJson] = useState("");
  const [paramsJsonErreur, setParamsJsonErreur] = useState("");
  const [batchLoading, setBatchLoading] = useState<"morning" | "day" | "all" | null>(null);
  const [batchResultat, setBatchResultat] = useState<JobBatchResponse | null>(null);
  const [schedulesEdition, setSchedulesEdition] = useState<Record<string, string>>({});
  const [logsTempsReel, setLogsTempsReel] = useState<LiveAdminLogEntry[]>([]);
  const [streamConnecte, setStreamConnecte] = useState(false);
  const [streamPause, setStreamPause] = useState(false);

  useEffect(() => {
    const token = obtenirTokenAdmin();
    if (!token) {
      setStreamConnecte(false);
      return;
    }

    const websocket = new WebSocket(
      `${obtenirWsAdminBaseUrl()}/api/v1/ws/admin/logs?token=${encodeURIComponent(token)}`,
    );

    websocket.onopen = () => setStreamConnecte(true);
    websocket.onclose = () => setStreamConnecte(false);
    websocket.onerror = () => setStreamConnecte(false);
    websocket.onmessage = (event) => {
      if (streamPause) {
        return;
      }
      try {
        const payload = JSON.parse(event.data) as LiveAdminLogEntry;
        if (!payload?.message || !payload?.timestamp) {
          return;
        }
        setLogsTempsReel((precedents) => [...precedents.slice(-79), payload]);
      } catch {
        // payload non JSON ignoré
      }
    };

    return () => {
      websocket.close();
    };
  }, [streamPause]);

  const {
    data: jobs,
    isLoading,
    refetch,
  } = utiliserRequete(["admin", "jobs"], async (): Promise<JobInfo[]> => {
    return listerJobs();
  });

  const { data: historique, isLoading: historiqueLoading } = utiliserRequete(
    [
      "admin",
      "jobs-history",
      String(pageHistorique),
      filtreJobId,
      filtreStatus,
      filtreDepuis,
      filtreJusqua,
    ],
    async (): Promise<JobHistoryResponse> => {
      const data = await listerHistoriqueJobs({
        page: pageHistorique,
        par_page: 20,
        job_id: filtreJobId || undefined,
        status: filtreStatus !== "all" ? filtreStatus : undefined,
        depuis: filtreDepuis ? `${filtreDepuis}T00:00:00` : undefined,
        jusqu_a: filtreJusqua ? `${filtreJusqua}T23:59:59` : undefined,
      });
      return data;
    },
  );

  const {
    data: comparaison,
    isLoading: comparaisonLoading,
    refetch: refetchComparaison,
  } = utiliserRequete(
    ["admin", "jobs-compare", "168h"],
    async (): Promise<JobCompareResponse> => comparerDryRunVsRun({ limite: 20, depuis_heures: 168 }),
  );

  const badgeHistorique = (status: string) => {
    if (status === "success") return <Badge>Succès</Badge>;
    if (status === "dry_run") return <Badge variant="secondary">Dry-run</Badge>;
    if (status === "failure") return <Badge variant="destructive">Échec</Badge>;
    if (status === "pending") return <Badge variant="outline">Pending</Badge>;
    return <Badge variant="outline">{status}</Badge>;
  };

  const parsParamsJson = (): Record<string, unknown> | null => {
    if (!paramsJson.trim()) return {};
    try {
      const parsed = JSON.parse(paramsJson) as unknown;
      if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
        setParamsJsonErreur("Les paramètres doivent être un objet JSON");
        return null;
      }
      setParamsJsonErreur("");
      return parsed as Record<string, unknown>;
    } catch {
      setParamsJsonErreur("JSON invalide");
      return null;
    }
  };

  const executerJob = async (jobId: string) => {
    const params = parsParamsJson();
    if (params === null) return; // JSON invalide
    setConfirmJobId(null);
    setRunStatuts((s) => ({ ...s, [jobId]: "running" }));
    try {
      await declencherJobAvecOptions(jobId, { dry_run: modeDryRun, force: modeForce, params });
      setRunStatuts((s) => ({ ...s, [jobId]: "success" }));
      // Rafraîchir les logs automatiquement après l'exécution
      chargerLogs(jobId);
      setTimeout(() => setRunStatuts((s) => ({ ...s, [jobId]: "idle" })), 3000);
    } catch {
      setRunStatuts((s) => ({ ...s, [jobId]: "error" }));
      setTimeout(() => setRunStatuts((s) => ({ ...s, [jobId]: "idle" })), 3000);
    }
  };

  const lancerTousLesJobs = async () => {
    setBatchLoading("all");
    try {
      const resultat = await executerTousLesJobs({
        dry_run: modeDryRun,
        continuer_sur_erreur: true,
        force: modeForce,
      });
      setBatchResultat(resultat);
      toast.success(`Exécution globale: ${resultat.succes} succès / ${resultat.echecs} échec(s)`);
      refetch();
      refetchComparaison();
    } catch {
      toast.error("Impossible d'exécuter tous les jobs");
    } finally {
      setBatchLoading(null);
    }
  };

  const lancerJobsMatin = async () => {
    setBatchLoading("morning");
    try {
      const resultat = await executerJobsDuMatin({
        dry_run: modeDryRun,
        continuer_sur_erreur: true,
      });
      setBatchResultat(resultat);
      toast.success(`Batch matin terminé: ${resultat.succes} succès / ${resultat.echecs} échec(s)`);
      refetch();
      refetchComparaison();
    } catch {
      toast.error("Erreur lors du lancement des jobs du matin");
    } finally {
      setBatchLoading(null);
    }
  };

  const simulerJournee = async () => {
    setBatchLoading("day");
    try {
      const resultat = await simulerJourneeJobs({
        dry_run: true,
        continuer_sur_erreur: true,
      });
      setBatchResultat(resultat);
      toast.success(`Simulation journée terminée: ${resultat.succes} succès / ${resultat.echecs} échec(s)`);
      refetchComparaison();
    } catch {
      toast.error("Erreur lors de la simulation de journée");
    } finally {
      setBatchLoading(null);
    }
  };

  const chargerLogs = async (jobId: string) => {
    setChargementLogs((s) => ({ ...s, [jobId]: true }));
    try {
      const { data } = await clientApi.get<JobLogsResponse>(`/admin/jobs/${jobId}/logs`);
      setJobLogs((s) => ({ ...s, [jobId]: data }));
    } catch {
      // silencieux
    } finally {
      setChargementLogs((s) => ({ ...s, [jobId]: false }));
    }
  };

  const toggleLogs = async (jobId: string) => {
    const ouvert = !jobLogsOuverts[jobId];
    setJobLogsOuverts((s) => ({ ...s, [jobId]: ouvert }));
    if (ouvert && !jobLogs[jobId]) {
      await chargerLogs(jobId);
    }
  };

  const sauvegarderSchedule = async (jobId: string) => {
    const cron = schedulesEdition[jobId]?.trim();
    if (!cron) return;
    try {
      const resultat = await mettreAJourScheduleJob(jobId, cron);
      toast.success(`Schedule mis à jour: ${resultat.schedule}`);
      refetch();
    } catch {
      toast.error("Impossible de mettre à jour le schedule");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Clock className="h-6 w-6" />
            Jobs planifiés
          </h1>
          <p className="text-muted-foreground">
            Gérez et déclenchez manuellement les tâches automatiques
          </p>
          <label className="mt-2 inline-flex items-center gap-2 text-xs text-muted-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={modeDryRun}
              onChange={(e) => setModeDryRun(e.target.checked)}
            />
            Mode dry-run (simulation)
          </label>
          <label className="mt-2 ml-4 inline-flex items-center gap-2 text-xs text-muted-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={modeForce}
              onChange={(e) => setModeForce(e.target.checked)}
            />
            Forcer l'exécution
          </label>
          <div className="mt-3">
            <textarea
              className="w-full max-w-xs rounded border border-input bg-background px-2 py-1.5 text-xs font-mono text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring resize-none"
              rows={3}
              placeholder='{"cle": "valeur"}'
              value={paramsJson}
              onChange={(e) => {
                setParamsJson(e.target.value);
                setParamsJsonErreur("");
              }}
              aria-label="Paramètres JSON personnalisés"
            />
            {paramsJsonErreur && (
              <p className="mt-1 text-xs text-destructive">{paramsJsonErreur}</p>
            )}
            {!paramsJsonErreur && paramsJson.trim() && (
              <p className="mt-1 text-xs text-muted-foreground">Params transmis dans le body de la requête</p>
            )}
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()} aria-label="Actualiser">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Liste des jobs</CardTitle>
          <CardDescription>
            {jobs ? `${jobs.length} job(s) enregistré(s)` : "Chargement…"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Chargement des jobs…
            </div>
          ) : !jobs || jobs.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">
              Aucun job actif (le scheduler n&apos;est peut-être pas démarré).
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Nom</TableHead>
                  <TableHead>Schedule</TableHead>
                  <TableHead>Prochain run</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job) => {
                  const runStatus = runStatuts[job.id] ?? "idle";
                  const logsOuverts = jobLogsOuverts[job.id] ?? false;
                  const logs = jobLogs[job.id];
                  const chargement = chargementLogs[job.id] ?? false;
                  return (
                    <Fragment key={job.id}>
                      <TableRow>
                        <TableCell className="font-mono text-xs text-muted-foreground">
                          {job.id}
                        </TableCell>
                        <TableCell className="font-medium">{job.nom}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          <div className="space-y-2">
                            <div>{job.schedule}</div>
                            <div className="flex gap-2">
                              <Input
                                value={schedulesEdition[job.id] ?? ""}
                                onChange={(e) => setSchedulesEdition((s) => ({ ...s, [job.id]: e.target.value }))}
                                placeholder="m h dom mon dow"
                                className="h-8 min-w-[180px] text-xs"
                              />
                              <Button size="sm" variant="ghost" onClick={() => void sauvegarderSchedule(job.id)}>
                                Sauver
                              </Button>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-sm">
                          {formaterDate(job.prochain_run)}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={job.statut === "actif" ? "default" : "secondary"}
                          >
                            {job.statut === "actif" ? (
                              <><CheckCircle2 className="mr-1 h-3 w-3" />Actif</>
                            ) : (
                              <><XCircle className="mr-1 h-3 w-3" />Inactif</>
                            )}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => toggleLogs(job.id)}
                              aria-label={`Logs ${job.nom}`}
                              title="Voir les logs"
                            >
                              {chargement ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <FileText className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              size="sm"
                              variant={
                                runStatus === "success"
                                  ? "default"
                                  : runStatus === "error"
                                  ? "destructive"
                                  : "outline"
                              }
                              disabled={runStatus === "running"}
                              onClick={() => setConfirmJobId(job.id)}
                              aria-label={`Exécuter ${job.nom}`}
                            >
                              {runStatus === "running" ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : runStatus === "success" ? (
                                <CheckCircle2 className="h-4 w-4" />
                              ) : runStatus === "error" ? (
                                <XCircle className="h-4 w-4" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                              <span className="ml-1.5 hidden sm:inline">
                                {runStatus === "running"
                                  ? "Exécution…"
                                  : runStatus === "success"
                                  ? "Terminé"
                                  : runStatus === "error"
                                  ? "Erreur"
                                  : "Exécuter"}
                              </span>
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                      {logsOuverts && (
                        <TableRow key={`${job.id}-logs`} className="bg-muted/30">
                          <TableCell colSpan={6} className="py-2 px-4">
                            {!logs || logs.logs.length === 0 ? (
                              <p className="text-xs text-muted-foreground italic py-1">
                                Aucune exécution manuelle enregistrée pour ce job.
                              </p>
                            ) : (
                              <div className="space-y-1">
                                <p className="text-xs font-medium text-muted-foreground mb-1">
                                  Dernières exécutions ({logs.total})
                                </p>
                                {logs.logs.map((log, i) => (
                                  <div key={i} className="flex items-start gap-2 text-xs">
                                    <span
                                      className={
                                        log.status === "succes"
                                          ? "text-green-600"
                                          : "text-red-500"
                                      }
                                    >
                                      {log.status === "succes" ? "✓" : "✗"}
                                    </span>
                                    <span className="text-muted-foreground shrink-0">
                                      {formaterDate(log.timestamp)}
                                    </span>
                                    <span>{log.message}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      )}
                    </Fragment>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Actions groupées Actions groupées</CardTitle>
          <CardDescription>
            Exécution groupée des jobs du matin et simulation d&apos;une journée type.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Button onClick={lancerJobsMatin} disabled={batchLoading !== null}>
              {batchLoading === "morning" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Lancer tous les jobs du matin
            </Button>
            <Button variant="outline" onClick={lancerTousLesJobs} disabled={batchLoading !== null}>
              {batchLoading === "all" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Tout exécuter
            </Button>
            <Button variant="outline" onClick={simulerJournee} disabled={batchLoading !== null}>
              {batchLoading === "day" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Clock className="mr-2 h-4 w-4" />}
              Simuler une journée (dry-run)
            </Button>
          </div>

          {batchResultat && (
            <div className="rounded-lg border p-3 text-sm">
              <p className="font-medium">
                Résultat: {batchResultat.succes} succès / {batchResultat.echecs} échec(s) ({batchResultat.total} job(s))
              </p>
              <p className="text-muted-foreground">Mode: {batchResultat.mode}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Logs temps réel</CardTitle>
          <CardDescription>
            Suivi live des exécutions admin et des jobs sans passer par la console.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <Badge variant={streamConnecte ? "default" : "destructive"}>
              {streamConnecte ? "Connecté" : "Déconnecté"}
            </Badge>
            <Button size="sm" variant="outline" onClick={() => setStreamPause((value) => !value)}>
              {streamPause ? "Reprendre" : "Pause"}
            </Button>
            <Button size="sm" variant="outline" onClick={() => setLogsTempsReel([])}>
              Vider
            </Button>
          </div>

          <div className="rounded-lg border bg-muted/20 p-3">
            {logsTempsReel.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                {streamConnecte ? "En attente de logs temps reel..." : "Aucun stream live disponible pour l'instant."}
              </p>
            ) : (
              <div className="max-h-72 space-y-2 overflow-y-auto font-mono text-xs">
                {logsTempsReel.slice().reverse().map((log, index) => (
                  <div key={`${log.timestamp}-${index}`} className="rounded border bg-background px-2 py-1">
                    <div className="flex flex-wrap items-center gap-2 text-muted-foreground">
                      <span>{formaterDate(log.timestamp)}</span>
                      <Badge variant={log.level === "ERROR" || log.level === "CRITICAL" ? "destructive" : "secondary"}>
                        {log.level}
                      </Badge>
                      <span>{log.module}</span>
                    </div>
                    <div className="mt-1 text-foreground">{log.message}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comparaison dry-run vs run</CardTitle>
          <CardDescription>
            Dernières comparaisons par job pour valider le passage en exécution réelle.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {comparaisonLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Chargement de la comparaison…
            </div>
          ) : !comparaison || comparaison.items.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucune donnée de comparaison disponible.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Job</TableHead>
                  <TableHead>Dry-run</TableHead>
                  <TableHead>Run réel</TableHead>
                  <TableHead>Delta durée</TableHead>
                  <TableHead>Statut</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {comparaison.items.map((item) => (
                  <TableRow key={item.job_id}>
                    <TableCell>
                      <div className="font-medium">{item.job_name}</div>
                      <div className="text-xs text-muted-foreground font-mono">{item.job_id}</div>
                    </TableCell>
                    <TableCell>{item.dry_run?.duration_ms ?? "—"} ms</TableCell>
                    <TableCell>{item.run?.duration_ms ?? "—"} ms</TableCell>
                    <TableCell>
                      {item.comparaison.delta_duration_ms === null ? "—" : `${item.comparaison.delta_duration_ms} ms`}
                    </TableCell>
                    <TableCell>
                      {item.comparaison.status_coherent === null ? (
                        <Badge variant="outline">N/A</Badge>
                      ) : item.comparaison.status_coherent ? (
                        <Badge>OK</Badge>
                      ) : (
                        <Badge variant="destructive">À vérifier</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Historique des exécutions</CardTitle>
          <CardDescription>
            Historique paginé des jobs avec filtres (statut, job, période)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2 md:grid-cols-5">
            <Input
              placeholder="Filtrer job_id"
              value={filtreJobId}
              onChange={(e) => {
                setPageHistorique(1);
                setFiltreJobId(e.target.value);
              }}
            />
            <Select
              value={filtreStatus}
              onValueChange={(value) => {
                setPageHistorique(1);
                setFiltreStatus(value);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Statut" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous statuts</SelectItem>
                <SelectItem value="success">Succès</SelectItem>
                <SelectItem value="failure">Échec</SelectItem>
                <SelectItem value="dry_run">Dry-run</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
            <Input
              type="date"
              value={filtreDepuis}
              onChange={(e) => {
                setPageHistorique(1);
                setFiltreDepuis(e.target.value);
              }}
            />
            <Input
              type="date"
              value={filtreJusqua}
              onChange={(e) => {
                setPageHistorique(1);
                setFiltreJusqua(e.target.value);
              }}
            />
            <Button
              variant="outline"
              onClick={() => {
                setPageHistorique(1);
                setFiltreJobId("");
                setFiltreStatus("all");
                setFiltreDepuis("");
                setFiltreJusqua("");
              }}
            >
              Réinitialiser
            </Button>
          </div>

          {historiqueLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Chargement de l'historique…
            </div>
          ) : !historique || historique.items.length === 0 ? (
            <p className="text-center py-8 text-muted-foreground">Aucune exécution trouvée.</p>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Job</TableHead>
                    <TableHead>Statut</TableHead>
                    <TableHead>Durée</TableHead>
                    <TableHead>Déclenché par</TableHead>
                    <TableHead>Message</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {historique.items.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="text-sm">{formaterDate(entry.started_at)}</TableCell>
                      <TableCell className="font-mono text-xs">{entry.job_id}</TableCell>
                      <TableCell>{badgeHistorique(entry.status)}</TableCell>
                      <TableCell>{entry.duration_ms} ms</TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {entry.triggered_by_user_id ?? "system"}
                      </TableCell>
                      <TableCell className="max-w-[420px] truncate text-xs">
                        {entry.error_message || entry.output_logs || "—"}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={async () => {
                            try {
                              await relancerJobDepuisHistorique(entry.id, { dry_run: modeDryRun, force: modeForce });
                              toast.success("Job relancé depuis l'historique");
                              refetch();
                            } catch {
                              toast.error("Impossible de relancer ce job");
                            }
                          }}
                        >
                          Relancer
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              <div className="flex items-center justify-between text-sm">
                <p className="text-muted-foreground">
                  {historique.total} exécution(s) • page {historique.page}/{historique.pages_totales}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={historique.page <= 1}
                    onClick={() => setPageHistorique((p) => Math.max(1, p - 1))}
                  >
                    Précédent
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={historique.page >= historique.pages_totales}
                    onClick={() => setPageHistorique((p) => p + 1)}
                  >
                    Suivant
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>

    {/* H4 — Dialog de confirmation avant exécution d'un job */}
    <Dialog open={confirmJobId !== null} onOpenChange={(open) => { if (!open) setConfirmJobId(null); }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirmer l'exécution</DialogTitle>
          <DialogDescription>
            {modeDryRun
              ? "Le job sera exécuté en mode simulation (aucune modification réelle)."
              : "Le job sera exécuté immédiatement. Cette action peut modifier des données."}
            {paramsJson.trim() && (
              <span className="mt-1 block text-xs font-mono">Params : {paramsJson}</span>
            )}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => setConfirmJobId(null)}>
            Annuler
          </Button>
          <Button
            variant={modeDryRun ? "secondary" : "default"}
            onClick={() => { if (confirmJobId) void executerJob(confirmJobId); }}
          >
            {modeDryRun ? "Simuler" : "Exécuter"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}