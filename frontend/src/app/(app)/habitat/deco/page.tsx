"use client";

import { listerProjetsDecoHabitat } from "@/bibliotheque/api/habitat";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";

export default function DecoHabitatPage() {
  const { data } = utiliserRequete(["habitat", "deco"], listerProjetsDecoHabitat);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Deco</h1>
        <p className="text-muted-foreground">Projets de decoration interieure par piece.</p>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Projets deco</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(data ?? []).map((projet) => (
            <div key={projet.id} className="rounded-md border p-3">
              <p className="font-medium">{projet.nom_piece}</p>
              <p className="text-xs text-muted-foreground">
                {projet.style ?? "style non defini"} · {projet.statut} · {projet.budget_prevu ?? "?"} EUR
              </p>
            </div>
          ))}
          {(data ?? []).length === 0 && <p className="text-sm text-muted-foreground">Aucun projet deco.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
