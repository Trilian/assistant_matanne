// ═══════════════════════════════════════════════════════════
// Page Admin — Jobs Cron
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
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
import { format, parseISO } from "date-fns";
import { fr } from "date-fns/locale";

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

type RunStatus = "idle" | "running" | "success" | "error";

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

  const {
    data: jobs,
    isLoading,
    refetch,
  } = utiliserRequete(["admin", "jobs"], async (): Promise<JobInfo[]> => {
    const { data } = await clientApi.get("/admin/jobs");
    return data;
  });

  const executerJob = async (jobId: string) => {
    setRunStatuts((s) => ({ ...s, [jobId]: "running" }));
    try {
      await clientApi.post(`/admin/jobs/${jobId}/run`);
      setRunStatuts((s) => ({ ...s, [jobId]: "success" }));
      // Rafraîchir les logs automatiquement après l'exécution
      chargerLogs(jobId);
      setTimeout(() => setRunStatuts((s) => ({ ...s, [jobId]: "idle" })), 3000);
    } catch {
      setRunStatuts((s) => ({ ...s, [jobId]: "error" }));
      setTimeout(() => setRunStatuts((s) => ({ ...s, [jobId]: "idle" })), 3000);
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
                    <>
                      <TableRow key={job.id}>
                        <TableCell className="font-mono text-xs text-muted-foreground">
                          {job.id}
                        </TableCell>
                        <TableCell className="font-medium">{job.nom}</TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {job.schedule}
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
                              onClick={() => executerJob(job.id)}
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
                    </>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}