"use client";

import { Wrench } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { listerArtisans, statsArtisans } from "@/bibliotheque/api/maison";

export default function PageArtisansMaison() {
  const { data: artisans = [], isLoading } = utiliserRequete(["maison", "artisans"], () => listerArtisans());
  const { data: stats } = utiliserRequete(["maison", "artisans", "stats"], statsArtisans);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">🔧 Artisans</h1>
        <p className="text-muted-foreground">Carnet d'adresses et suivi des interventions</p>
      </div>

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.total_artisans ?? 0}</p><p className="text-xs text-muted-foreground">Artisans</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.nb_metiers ?? 0}</p><p className="text-xs text-muted-foreground">Métiers</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{(stats.depenses_totales ?? 0).toFixed(0)} €</p><p className="text-xs text-muted-foreground">Dépenses</p></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><p className="text-2xl font-bold">{stats.nb_interventions ?? 0}</p><p className="text-xs text-muted-foreground">Interventions</p></CardContent></Card>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Liste des artisans</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {isLoading ? (
            <div className="space-y-2">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-14" />)}</div>
          ) : artisans.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucun artisan enregistré.</p>
          ) : (
            artisans.map((artisan) => (
              <div key={artisan.id} className="rounded-md border p-3 flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="font-medium truncate">{artisan.nom}</p>
                  <p className="text-xs text-muted-foreground truncate">{artisan.metier ?? "Métier non précisé"}</p>
                </div>
                <div className="flex items-center gap-2">
                  {artisan.note_moyenne != null && <Badge variant="outline">⭐ {artisan.note_moyenne.toFixed(1)}</Badge>}
                  <Wrench className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
