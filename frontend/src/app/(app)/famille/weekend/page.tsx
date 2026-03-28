"use client";

import { useMutation } from "@tanstack/react-query";
import { Calendar, MapPin, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { convertirWeekendEnActivite, listerActivites } from "@/bibliotheque/api/famille";

type ActiviteAffichable = {
  id: number;
  titre: string;
  lieu?: string;
  date?: string;
};

export default function PageWeekend() {
  const { data: activites = [], isLoading } = utiliserRequete<ActiviteAffichable[]>(
    ["famille", "weekend", "activites"],
    () => listerActivites()
  );

  const mutationConversion = useMutation({
    mutationFn: (activiteId: number) => convertirWeekendEnActivite(activiteId),
    onSuccess: () => {
      toast.success("Activité convertie vers le module Famille.");
    },
    onError: () => {
      toast.error("Impossible de convertir cette activité.");
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Weekend</h1>
        <p className="text-muted-foreground">Préparer et convertir vos idées du week-end.</p>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Ce week-end</h2>

        {isLoading ? (
          <div className="text-sm text-muted-foreground">Chargement des activités...</div>
        ) : activites.length === 0 ? (
          <div className="text-sm text-muted-foreground">Aucune activité prévue.</div>
        ) : (
          <div className="grid gap-3">
            {activites.map((activite) => (
              <Card key={activite.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-green-600" />
                    {activite.titre}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {activite.lieu && (
                    <div className="text-sm text-muted-foreground flex items-center gap-1.5">
                      <MapPin className="h-3.5 w-3.5" />
                      {activite.lieu}
                    </div>
                  )}

                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => mutationConversion.mutate(activite.id)}
                    disabled={mutationConversion.isPending}
                  >
                    {mutationConversion.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Convertir en activité famille
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
