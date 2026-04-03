"use client";

import { Download, NotebookText } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { obtenirJournalFamilialAuto, obtenirJournalFamilialPdf, telechargerPdfBase64 } from "@/bibliotheque/api/avance";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Badge } from "@/composants/ui/badge";
import { toast } from "sonner";

export default function PageJournal() {
  const { data, isLoading } = utiliserRequete(
    ["famille", "journal-familial-auto", "page"],
    obtenirJournalFamilialAuto,
    { staleTime: 10 * 60 * 1000 }
  );

  const mutationTelecharger = useMutation({
    mutationFn: obtenirJournalFamilialPdf,
    onSuccess: (payload) => {
      telechargerPdfBase64(payload.contenu_base64, payload.filename);
      toast.success("Journal familial téléchargé");
    },
    onError: () => toast.error("Impossible de télécharger le journal familial"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <NotebookText className="h-6 w-6" />
          Journal familial
        </h1>
        <p className="text-muted-foreground">Résumé automatique de la semaine familiale, avec export PDF.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{data?.titre ?? "Journal familial"}</CardTitle>
          <CardDescription>{data?.semaine_reference ?? "Semaine en cours"}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading ? (
            <p className="text-sm text-muted-foreground">Chargement du journal…</p>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">{data?.resume ?? "Aucun journal disponible pour le moment."}</p>

              {!!data?.faits_marquants?.length && (
                <section className="space-y-2">
                  <h2 className="text-sm font-medium">Faits marquants</h2>
                  <div className="flex flex-wrap gap-2">
                    {data.faits_marquants.map((item) => (
                      <Badge key={item} variant="secondary">{item}</Badge>
                    ))}
                  </div>
                </section>
              )}

              {!!data?.moments_joyeux?.length && (
                <section className="space-y-2">
                  <h2 className="text-sm font-medium">Moments joyeux</h2>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {data.moments_joyeux.map((item) => (
                      <li key={item}>• {item}</li>
                    ))}
                  </ul>
                </section>
              )}

              {!!data?.points_attention?.length && (
                <section className="space-y-2">
                  <h2 className="text-sm font-medium">Points d'attention</h2>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    {data.points_attention.map((item) => (
                      <li key={item}>• {item}</li>
                    ))}
                  </ul>
                </section>
              )}
            </>
          )}

          <Button onClick={() => mutationTelecharger.mutate()} disabled={mutationTelecharger.isPending}>
            <Download className="mr-2 h-4 w-4" />
            Télécharger le PDF
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
