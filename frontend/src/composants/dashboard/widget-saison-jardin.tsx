"use client";

import { useQuery } from "@tanstack/react-query";
import { Sprout, Sparkles } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { obtenirWidgetSaisonJardin, type WidgetSaisonJardinResponse } from "@/bibliotheque/api/bridges";

const PRIORITE_STYLES: Record<string, string> = {
  haute: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  moyenne: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  basse: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
};

export function WidgetSaisonJardin() {
  const { data, isLoading, error } = useQuery<WidgetSaisonJardinResponse>({
    queryKey: ["dashboard", "saison-jardin"],
    queryFn: obtenirWidgetSaisonJardin,
    staleTime: 30 * 60 * 1000,
    refetchInterval: 60 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Sprout className="h-4 w-4" />
            Saison jardin
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Chargement...</p>
        </CardContent>
      </Card>
    );
  }

  if (error || !data || (data.activites?.length ?? 0) === 0) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Sprout className="h-4 w-4" />
            Saison jardin
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Aucune activité saisonnière</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-green-300/50 bg-green-50/50 dark:border-green-900/40 dark:bg-green-950/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Sprout className="h-4 w-4 text-green-600" />
          Jardin — {data.saison}
        </CardTitle>
        <CardDescription>{data.mois}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {(data.activites ?? []).slice(0, 4).map((activite, i) => (
          <div
            key={`${activite.type}-${i}`}
            className="rounded-md border bg-background/70 px-3 py-2"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium">{activite.description}</p>
              <Badge
                variant="secondary"
                className={`text-xs shrink-0 ${PRIORITE_STYLES[activite.priorite] ?? ""}`}
              >
                {activite.priorite}
              </Badge>
            </div>
            {activite.plantes_concernees.length > 0 && (
              <p className="text-xs text-muted-foreground mt-1">
                {activite.plantes_concernees.join(", ")}
              </p>
            )}
          </div>
        ))}
        {data.conseil_ia && (
          <div className="flex items-start gap-2 rounded-md border border-green-200/70 bg-background/70 p-2 text-xs">
            <Sparkles className="h-3 w-3 mt-0.5 text-green-600 shrink-0" />
            <p className="text-muted-foreground">{data.conseil_ia}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
