"use client";

import { useQuery } from "@tanstack/react-query";
import { Home, TrendingUp } from "lucide-react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { obtenirWidgetVeilleImmo, type WidgetVeilleImmoResponse } from "@/bibliotheque/api/bridges";

export function WidgetVeilleImmo() {
  const { data, isLoading, error } = useQuery<WidgetVeilleImmoResponse>({
    queryKey: ["dashboard", "veille-immo"],
    queryFn: obtenirWidgetVeilleImmo,
    staleTime: 10 * 60 * 1000,
    refetchInterval: 30 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Home className="h-4 w-4" />
            Veille immobilière
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Chargement...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data || data.total_actives === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Home className="h-4 w-4" />
            Veille immobilière
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Aucune annonce en veille</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-violet-300/50 bg-violet-50/50 dark:border-violet-900/40 dark:bg-violet-950/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Home className="h-4 w-4 text-violet-600" />
          Veille immobilière
          <Badge variant="secondary" className="ml-auto text-xs">
            {data.total_actives} active{data.total_actives > 1 ? "s" : ""}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {data.prix_moyen && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <TrendingUp className="h-3 w-3" />
            Prix moyen : {data.prix_moyen.toLocaleString("fr-FR")} €
          </div>
        )}
        {(data.annonces_recentes ?? []).slice(0, 3).map((annonce) => (
          <Link
            key={annonce.id}
            href="/maison/projets"
            className="flex items-center gap-2 rounded-md p-2 hover:bg-accent transition-colors"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{annonce.titre}</p>
              <p className="text-xs text-muted-foreground">
                {annonce.ville} · {annonce.surface ? `${annonce.surface} m²` : ""}
              </p>
            </div>
            <span className="text-sm font-semibold shrink-0">
              {annonce.prix.toLocaleString("fr-FR")} €
            </span>
          </Link>
        ))}
        {data.total_actives > 3 && (
          <Link
            href="/maison/projets"
            className="block text-xs text-primary hover:underline text-center pt-1"
          >
            Voir les {data.total_actives} annonces
          </Link>
        )}
      </CardContent>
    </Card>
  );
}
