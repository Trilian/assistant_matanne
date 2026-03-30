"use client";

import { listerZonesJardinHabitat } from "@/bibliotheque/api/habitat";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function JardinHabitatPage() {
  const { data } = utiliserRequete(["habitat", "jardin", "zones"], () => listerZonesJardinHabitat());

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Jardin Habitat</h1>
        <p className="text-muted-foreground">Zonage paysager du terrain et budget par zone.</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Zones</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(data ?? []).map((zone) => (
            <div key={zone.id} className="rounded-md border p-3">
              <p className="font-medium">{zone.nom}</p>
              <p className="text-xs text-muted-foreground">
                {zone.type_zone ?? "type libre"} · {zone.surface_m2 ?? "?"} m2 · {zone.budget_estime ?? "?"} EUR
              </p>
            </div>
          ))}
          {(data ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucune zone jardin.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
