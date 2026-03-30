"use client";

import type { ReactNode } from "react";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent } from "@/composants/ui/card";

interface StatHabitat {
  label: string;
  valeur: string;
}

interface EntetePageHabitatProps {
  badge?: string;
  titre: string;
  description: string;
  stats?: StatHabitat[];
  actions?: ReactNode;
}

export function EntetePageHabitat({ badge, titre, description, stats, actions }: EntetePageHabitatProps) {
  return (
    <Card className="overflow-hidden border-emerald-200/70 bg-[linear-gradient(135deg,rgba(240,253,244,0.96),rgba(255,251,235,0.92))] shadow-sm dark:border-emerald-900/60 dark:bg-[linear-gradient(135deg,rgba(6,20,18,0.96),rgba(34,24,10,0.92))]">
      <CardContent className="flex flex-col gap-6 p-6 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-3">
          {badge ? <Badge variant="secondary" className="w-fit bg-white/80 text-emerald-900 dark:bg-white/10 dark:text-emerald-100">{badge}</Badge> : null}
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold tracking-tight">{titre}</h1>
            <p className="max-w-3xl text-sm leading-6 text-muted-foreground">{description}</p>
          </div>
          {stats && stats.length > 0 ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {stats.map((stat) => (
                <div key={stat.label} className="rounded-2xl border border-white/60 bg-white/70 px-4 py-3 backdrop-blur dark:border-white/10 dark:bg-white/5">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">{stat.label}</p>
                  <p className="mt-1 text-xl font-semibold">{stat.valeur}</p>
                </div>
              ))}
            </div>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div> : null}
      </CardContent>
    </Card>
  );
}