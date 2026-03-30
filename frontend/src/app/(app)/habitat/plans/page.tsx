"use client";

import { listerPlansHabitat } from "@/bibliotheque/api/habitat";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function PlansHabitatPage() {
  const { data } = utiliserRequete(["habitat", "plans"], listerPlansHabitat);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Plans</h1>
        <p className="text-muted-foreground">Gestion des plans importes et des versions.</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Plans enregistres</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(data ?? []).map((plan) => (
            <div key={plan.id} className="rounded-md border p-3">
              <p className="font-medium">{plan.nom}</p>
              <p className="text-xs text-muted-foreground">
                {plan.type_plan} · v{plan.version} · {plan.surface_totale_m2 ?? "?"} m2
              </p>
            </div>
          ))}
          {(data ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucun plan disponible.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
