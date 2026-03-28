// ═══════════════════════════════════════════════════════════
// Page Admin — Jobs Cron
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { Play, RefreshCw, Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
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
      setTimeout(() => setRunStatuts((s) => ({ ...s, [jobId]: "idle" })), 3000);
    } catch {
      setRunStatuts((s) => ({ ...s, [jobId]: "error" }));
      setTimeout(() => setRunStatuts((s) => ({ ...s, [jobId]: "idle" })), 3000);
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
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {jobs.map((job) => {
                  const runStatus = runStatuts[job.id] ?? "idle";
                  return (
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
                      </TableCell>
                    </TableRow>
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
