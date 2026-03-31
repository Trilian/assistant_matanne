"use client";

import { useCallback, useEffect, useState } from "react";
import { Shield, X, RefreshCw, Play, Activity } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { utiliserAuth } from "@/crochets/utiliser-auth";
import {
  basculerModeMaintenance,
  listerJobs,
  lireFeatureFlags,
  lireModeMaintenance,
  obtenirLiveSnapshotAdmin,
} from "@/bibliotheque/api/admin";

export function PanneauAdminFlottant() {
  const { utilisateur } = utiliserAuth();
  const estAdmin = utilisateur?.role === "admin";

  const [ouvert, setOuvert] = useState(false);
  const [maintenance, setMaintenance] = useState(false);
  const [loading, setLoading] = useState(false);
  const [jobsCount, setJobsCount] = useState(0);
  const [flagsCount, setFlagsCount] = useState(0);
  const [requestsTotal, setRequestsTotal] = useState(0);
  const [aiQuota, setAiQuota] = useState("n/a");

  const charger = useCallback(async () => {
    if (!estAdmin) return;
    setLoading(true);
    try {
      const [jobs, flags, snapshot, maintenanceResp] = await Promise.all([
        listerJobs(),
        lireFeatureFlags(),
        obtenirLiveSnapshotAdmin(),
        lireModeMaintenance(),
      ]);
      setJobsCount(jobs.length);
      setFlagsCount(flags.total);
      setRequestsTotal(snapshot.api.requests_total);
      const ai = snapshot.api.ai as { daily_used?: number; daily_limit?: number };
      if (ai?.daily_limit) {
        setAiQuota(`${ai.daily_used ?? 0}/${ai.daily_limit}`);
      } else {
        setAiQuota("n/a");
      }
      setMaintenance(maintenanceResp.maintenance_mode);
    } finally {
      setLoading(false);
    }
  }, [estAdmin]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (!estAdmin) return;
      if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === "a") {
        event.preventDefault();
        setOuvert((prev) => !prev);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [estAdmin]);

  useEffect(() => {
    if (ouvert && estAdmin) {
      charger();
    }
  }, [ouvert, estAdmin, charger]);

  if (!estAdmin) return null;

  return (
    <>
      <button
        type="button"
        onClick={() => setOuvert((prev) => !prev)}
        className="fixed bottom-20 right-4 z-40 rounded-full border bg-background p-2 shadow md:bottom-6"
        aria-label="Ouvrir le panneau admin flottant"
      >
        <Shield className="h-5 w-5" />
      </button>

      {ouvert && (
        <div className="fixed inset-0 z-50 bg-black/30 p-4 md:p-8" onClick={() => setOuvert(false)}>
          <Card className="ml-auto w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-base flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Panneau Admin
              </CardTitle>
              <Button size="icon" variant="ghost" onClick={() => setOuvert(false)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="rounded border p-2">
                  <p className="text-muted-foreground">Jobs</p>
                  <p className="font-semibold">{jobsCount}</p>
                </div>
                <div className="rounded border p-2">
                  <p className="text-muted-foreground">Feature flags</p>
                  <p className="font-semibold">{flagsCount}</p>
                </div>
                <div className="rounded border p-2">
                  <p className="text-muted-foreground">Requêtes API</p>
                  <p className="font-semibold">{requestsTotal}</p>
                </div>
                <div className="rounded border p-2">
                  <p className="text-muted-foreground">Quota IA</p>
                  <p className="font-semibold">{aiQuota}</p>
                </div>
              </div>

              <div className="flex items-center justify-between rounded border p-2">
                <div>
                  <p className="text-sm font-medium">Mode maintenance</p>
                  <p className="text-xs text-muted-foreground">Bandeau global utilisateur</p>
                </div>
                <Button
                  variant={maintenance ? "destructive" : "outline"}
                  size="sm"
                  onClick={async () => {
                    const next = !maintenance;
                    setMaintenance(next);
                    try {
                      await basculerModeMaintenance(next);
                    } catch {
                      setMaintenance(!next);
                    }
                  }}
                >
                  {maintenance ? "ON" : "OFF"}
                </Button>
              </div>

              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={charger} disabled={loading}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
                <Button size="sm" variant="outline" asChild>
                  <a href="/admin/jobs">
                    <Play className="mr-2 h-4 w-4" />
                    Jobs
                  </a>
                </Button>
                <Button size="sm" variant="outline" asChild>
                  <a href="/admin/services">
                    <Activity className="mr-2 h-4 w-4" />
                    Santé
                  </a>
                </Button>
              </div>

              <Badge variant="secondary">Ctrl+Shift+A</Badge>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}
