// ═══════════════════════════════════════════════════════════
// Page Admin — Scheduler Visuel CRON (D2)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useMemo } from "react";
import {
  Clock,
  RefreshCw,
  Play,
  Filter,
  Calendar,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/composants/ui/select";
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
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { format, parseISO, differenceInMinutes } from "date-fns";
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

/** Classifie un job par domaine selon son ID */
function categoriserJob(id: string): string {
  if (id.includes("famille") || id.includes("jules") || id.includes("anniversaire") || id.includes("vaccin") || id.includes("bien_etre") || id.includes("points_famille"))
    return "Famille";
  if (id.includes("recette") || id.includes("courses") || id.includes("nutrition") || id.includes("peremption") || id.includes("batch") || id.includes("gaspillage") || id.includes("openfoodfacts") || id.includes("stock") || id.includes("inventaire") || id.includes("prediction_courses"))
    return "Cuisine";
  if (id.includes("jardin") || id.includes("recolte") || id.includes("maison") || id.includes("entretien") || id.includes("energie") || id.includes("charge") || id.includes("habitat") || id.includes("projet"))
    return "Maison";
  if (id.includes("jeux") || id.includes("loto") || id.includes("tirage") || id.includes("pari"))
    return "Jeux";
  if (id.includes("budget") || id.includes("depense"))
    return "Budget";
  if (id.includes("notification") || id.includes("digest") || id.includes("push") || id.includes("whatsapp") || id.includes("rappel_courses"))
    return "Notifications";
  if (id.includes("garmin") || id.includes("meteo") || id.includes("calendrier") || id.includes("google") || id.includes("sync"))
    return "Sync";
  if (id.includes("nettoyage") || id.includes("purge") || id.includes("backup") || id.includes("archive") || id.includes("cache") || id.includes("log") || id.includes("sante") || id.includes("automation"))
    return "Système";
  return "Autre";
}

const COULEURS_CATEGORIES: Record<string, string> = {
  Famille: "#8b5cf6",
  Cuisine: "#f59e0b",
  Maison: "#10b981",
  Jeux: "#ec4899",
  Budget: "#3b82f6",
  Notifications: "#06b6d4",
  Sync: "#6366f1",
  Système: "#6b7280",
  Autre: "#9ca3af",
};

function formaterDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return format(parseISO(iso), "dd/MM HH:mm", { locale: fr });
  } catch {
    return iso;
  }
}

function tempRestant(iso: string | null): string {
  if (!iso) return "—";
  try {
    const d = parseISO(iso);
    const mins = differenceInMinutes(d, new Date());
    if (mins < 0) return "passé";
    if (mins < 60) return `${mins} min`;
    const heures = Math.floor(mins / 60);
    if (heures < 24) return `${heures}h${mins % 60 > 0 ? String(mins % 60).padStart(2, "0") : ""}`;
    const jours = Math.floor(heures / 24);
    return `${jours}j ${heures % 24}h`;
  } catch {
    return "—";
  }
}

export default function PageAdminScheduler() {
  const [filtre, setFiltre] = useState("");
  const [categorie, setCategorie] = useState<string>("all");
  const [runStatuts, setRunStatuts] = useState<Record<string, RunStatus>>({});

  const {
    data: jobs,
    isLoading,
    refetch,
  } = utiliserRequete<JobInfo[]>(["admin", "jobs", "scheduler"], () =>
    clientApi.get("/api/v1/admin/jobs").then((r) => r.data)
  );

  const jobsEnrichis = useMemo(() => {
    if (!jobs) return [];
    return jobs.map((j) => ({
      ...j,
      categorie: categoriserJob(j.id),
    }));
  }, [jobs]);

  const jobsFiltres = useMemo(() => {
    let result = jobsEnrichis;
    if (filtre) {
      const f = filtre.toLowerCase();
      result = result.filter(
        (j) =>
          j.id.toLowerCase().includes(f) ||
          j.nom.toLowerCase().includes(f)
      );
    }
    if (categorie !== "all") {
      result = result.filter((j) => j.categorie === categorie);
    }
    return result;
  }, [jobsEnrichis, filtre, categorie]);

  // Stats par catégorie pour le graphique
  const statsCategories = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const j of jobsEnrichis) {
      counts[j.categorie] = (counts[j.categorie] || 0) + 1;
    }
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [jobsEnrichis]);

  const triggerJob = async (jobId: string) => {
    setRunStatuts((prev) => ({ ...prev, [jobId]: "running" }));
    try {
      await clientApi.post(`/api/v1/admin/jobs/${jobId}/run`);
      setRunStatuts((prev) => ({ ...prev, [jobId]: "success" }));
      setTimeout(() => setRunStatuts((prev) => ({ ...prev, [jobId]: "idle" })), 3000);
    } catch {
      setRunStatuts((prev) => ({ ...prev, [jobId]: "error" }));
      setTimeout(() => setRunStatuts((prev) => ({ ...prev, [jobId]: "idle" })), 3000);
    }
  };

  const categories = useMemo(() => {
    const cats = new Set(jobsEnrichis.map((j) => j.categorie));
    return Array.from(cats).sort();
  }, [jobsEnrichis]);

  return (
    <div className="space-y-4">
      {/* En-tête stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Card>
          <CardContent className="pt-4 pb-3 text-center">
            <div className="text-2xl font-bold">{jobsEnrichis.length}</div>
            <div className="text-xs text-muted-foreground">Jobs total</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 pb-3 text-center">
            <div className="text-2xl font-bold text-green-600">
              {jobsEnrichis.filter((j) => j.statut === "actif").length}
            </div>
            <div className="text-xs text-muted-foreground">Actifs</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 pb-3 text-center">
            <div className="text-2xl font-bold">{categories.length}</div>
            <div className="text-xs text-muted-foreground">Catégories</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 pb-3 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {jobsEnrichis.filter((j) => j.prochain_run).length}
            </div>
            <div className="text-xs text-muted-foreground">Planifiés</div>
          </CardContent>
        </Card>
      </div>

      {/* Graphique par catégorie */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Répartition par domaine
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statsCategories} layout="vertical">
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {statsCategories.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={COULEURS_CATEGORIES[entry.name] || "#9ca3af"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Table des jobs */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Scheduler CRON
            </CardTitle>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Rafraîchir
            </Button>
          </div>
          <CardDescription>
            Timeline de tous les jobs CRON avec prochain run et catégorie
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filtres */}
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="Rechercher un job..."
              value={filtre}
              onChange={(e) => setFiltre(e.target.value)}
              className="max-w-xs"
            />
            <Select value={categorie} onValueChange={setCategorie}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes ({jobsEnrichis.length})</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat} ({jobsEnrichis.filter((j) => j.categorie === cat).length})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin mr-2" />
              Chargement des jobs...
            </div>
          ) : (
            <div className="border rounded-lg overflow-auto max-h-[600px]">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10">#</TableHead>
                    <TableHead>Job</TableHead>
                    <TableHead>Catégorie</TableHead>
                    <TableHead>Schedule</TableHead>
                    <TableHead>Prochain run</TableHead>
                    <TableHead>Dans</TableHead>
                    <TableHead>Dernier run</TableHead>
                    <TableHead className="w-20">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobsFiltres.map((job, idx) => (
                    <TableRow key={job.id}>
                      <TableCell className="text-muted-foreground text-xs">
                        {idx + 1}
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-mono text-sm">{job.id}</div>
                          <div className="text-xs text-muted-foreground">{job.nom}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          style={{
                            borderColor: COULEURS_CATEGORIES[job.categorie],
                            color: COULEURS_CATEGORIES[job.categorie],
                          }}
                        >
                          {job.categorie}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {job.schedule}
                      </TableCell>
                      <TableCell className="text-sm">
                        {formaterDate(job.prochain_run)}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {tempRestant(job.prochain_run)}
                      </TableCell>
                      <TableCell className="text-sm">
                        {formaterDate(job.dernier_run)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => triggerJob(job.id)}
                          disabled={
                            runStatuts[job.id] === "running"
                          }
                        >
                          {runStatuts[job.id] === "running" ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : runStatuts[job.id] === "success" ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          ) : runStatuts[job.id] === "error" ? (
                            <XCircle className="h-4 w-4 text-red-500" />
                          ) : (
                            <Play className="h-4 w-4" />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
