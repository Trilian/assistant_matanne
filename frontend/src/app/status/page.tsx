"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";

interface ServiceStatus {
  status: string;
  latency_ms: number;
  details?: string | null;
}

interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  services: Record<string, ServiceStatus>;
  uptime_seconds: number;
}

function badgeVariant(statut: string): "default" | "secondary" | "destructive" {
  if (statut === "healthy" || statut === "ok") {
    return "default";
  }
  if (statut === "degraded" || statut === "warning") {
    return "secondary";
  }
  return "destructive";
}

function formaterUptime(secondes: number): string {
  const h = Math.floor(secondes / 3600);
  const m = Math.floor((secondes % 3600) / 60);
  return `${h}h ${m}m`;
}

export default function StatusPage() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);

  useEffect(() => {
    let annule = false;

    const charger = async () => {
      try {
        const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
        const reponse = await fetch(`${base}/status`, { cache: "no-store" });
        if (!reponse.ok) {
          throw new Error(`Status HTTP ${reponse.status}`);
        }
        const json = (await reponse.json()) as HealthResponse;
        if (!annule) {
          setData(json);
          setErreur(null);
        }
      } catch (e) {
        if (!annule) {
          setErreur(e instanceof Error ? e.message : "Erreur inconnue");
        }
      }
    };

    charger();
    const id = window.setInterval(charger, 30000);
    return () => {
      annule = true;
      window.clearInterval(id);
    };
  }, []);

  return (
    <main className="mx-auto w-full max-w-4xl space-y-6 p-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Status système</h1>
        <p className="text-muted-foreground">Disponibilité backend et latence des services internes.</p>
      </header>

      {erreur ? (
        <Card>
          <CardHeader>
            <CardTitle>Indisponible</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-600">{erreur}</p>
          </CardContent>
        </Card>
      ) : null}

      {data ? (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Statut global</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge variant={badgeVariant(data.status)}>{data.status}</Badge>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Uptime</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold">{formaterUptime(data.uptime_seconds)}</span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Version API</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold">{data.version}</span>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Services</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(data.services).map(([nom, service]) => (
                  <div key={nom} className="flex items-center justify-between rounded-md border p-3">
                    <div>
                      <p className="font-medium">{nom}</p>
                      {service.details ? (
                        <p className="text-xs text-muted-foreground">{service.details}</p>
                      ) : null}
                    </div>
                    <div className="text-right">
                      <Badge variant={badgeVariant(service.status)}>{service.status}</Badge>
                      <p className="mt-1 text-xs text-muted-foreground">{service.latency_ms} ms</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      ) : null}
    </main>
  );
}
