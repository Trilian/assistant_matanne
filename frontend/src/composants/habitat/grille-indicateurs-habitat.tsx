"use client";

import { Card, CardContent } from "@/composants/ui/card";

interface DonneesHabitatHub {
  scenarios: number;
  annonces: number;
  plans: number;
  projets_deco: number;
  zones_jardin: number;
  alertes: number;
  annonces_a_traiter: number;
  budget_deco_depense: number;
  budget_deco_total: number;
}

interface GrilleIndicateursHabitatProps {
  data: DonneesHabitatHub;
}

export function GrilleIndicateursHabitat({ data }: GrilleIndicateursHabitatProps) {
  return (
    <div className="grid gap-3 grid-cols-2 md:grid-cols-4 xl:grid-cols-8">
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.scenarios}</p><p className="text-xs text-muted-foreground">Scenarios</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.annonces}</p><p className="text-xs text-muted-foreground">Annonces</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.plans}</p><p className="text-xs text-muted-foreground">Plans</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.projets_deco}</p><p className="text-xs text-muted-foreground">Projets deco</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.zones_jardin}</p><p className="text-xs text-muted-foreground">Zones jardin</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.alertes}</p><p className="text-xs text-muted-foreground">Alertes</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{data.annonces_a_traiter}</p><p className="text-xs text-muted-foreground">A traiter</p></CardContent></Card>
      <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{Math.round((data.budget_deco_depense / Math.max(data.budget_deco_total || 1, 1)) * 100)}%</p><p className="text-xs text-muted-foreground">Budget deco consomme</p></CardContent></Card>
    </div>
  );
}
