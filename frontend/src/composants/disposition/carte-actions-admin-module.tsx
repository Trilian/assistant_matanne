"use client";

import Link from "next/link";
import { useState } from "react";
import { Flag, FlaskConical, Loader2, Play, Shield, Settings2 } from "lucide-react";
import { toast } from "sonner";
import { declencherJobAvecOptions } from "@/bibliotheque/api/admin";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import { Badge } from "@/composants/ui/badge";
import { Button } from "@/composants/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/composants/ui/card";

export interface ActionJobAdminModule {
  id: string;
  label: string;
  hint?: string;
}

interface CarteActionsAdminModuleProps {
  moduleLabel: string;
  description?: string;
  jobs: ActionJobAdminModule[];
}

export function CarteActionsAdminModule({
  moduleLabel,
  description,
  jobs,
}: CarteActionsAdminModuleProps) {
  const { utilisateur } = utiliserAuth();
  const [jobEnCours, setJobEnCours] = useState<string | null>(null);

  if (utilisateur?.role !== "admin" || jobs.length === 0) {
    return null;
  }

  const lancerJob = async (job: ActionJobAdminModule) => {
    setJobEnCours(job.id);
    try {
      const resultat = await declencherJobAvecOptions(job.id, {
        dry_run: false,
        force: true,
      });
      toast.success(`${job.label} lancé`, {
        description: resultat.message,
      });
    } catch {
      toast.error(`Impossible de lancer ${job.label}`);
    } finally {
      setJobEnCours(null);
    }
  };

  return (
    <Card className="border-dashed border-sky-500/40 bg-sky-500/5">
      <CardHeader className="pb-3">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <CardTitle className="flex items-center gap-2 text-base">
              <Shield className="h-4 w-4 text-sky-600" />
              Actions admin — {moduleLabel}
            </CardTitle>
            <CardDescription>
              {description ?? "Déclenchement manuel des jobs critiques du module et accès rapides admin."}
            </CardDescription>
          </div>
          <Badge variant="secondary">Admin</Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
          {jobs.map((job) => {
            const enCours = jobEnCours === job.id;
            return (
              <Button
                key={job.id}
                type="button"
                variant="outline"
                className="h-auto items-start justify-start whitespace-normal text-left"
                onClick={() => void lancerJob(job)}
                disabled={enCours}
              >
                <div className="flex items-start gap-2">
                  {enCours ? (
                    <Loader2 className="mt-0.5 h-4 w-4 animate-spin text-sky-600" />
                  ) : (
                    <Play className="mt-0.5 h-4 w-4 text-sky-600" />
                  )}
                  <span>
                    <span className="block font-medium">{job.label}</span>
                    <span className="block text-xs text-muted-foreground">
                      {job.hint ?? job.id}
                    </span>
                  </span>
                </div>
              </Button>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-2">
          <Button asChild size="sm" variant="outline">
            <Link href="/admin/jobs">
              <Settings2 className="mr-1.5 h-4 w-4" />
              Scheduler complet
            </Link>
          </Button>
          <Button asChild size="sm" variant="outline">
            <Link href="/admin/services">
              <FlaskConical className="mr-1.5 h-4 w-4" />
              Dashboard live & seed
            </Link>
          </Button>
          <Button asChild size="sm" variant="outline">
            <Link href="/admin/feature-flags">
              <Flag className="mr-1.5 h-4 w-4" />
              Feature flags
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
