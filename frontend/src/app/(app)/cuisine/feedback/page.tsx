// ═══════════════════════════════════════════════════════════
// Feedback de fin de semaine
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Star, Send, Loader2, CheckCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Textarea } from "@/composants/ui/textarea";
import { envoyerFeedbackSemaine, type FeedbackItem } from "@/bibliotheque/api/ia-bridges";
import { clientApi } from "@/bibliotheque/api/client";

interface RepasData {
  id: number;
  type_repas: string;
  recette_nom: string;
  recette_id: number;
  date_repas: string;
}

export default function FeedbackSemainePage() {
  const [feedbacks, setFeedbacks] = useState<Record<number, FeedbackItem>>({});
  const [envoye, setEnvoye] = useState(false);

  // Charger les repas de la semaine
  const repasQuery = useQuery({
    queryKey: ["repas-semaine-feedback"],
    queryFn: async () => {
      const { data } = await clientApi.get<RepasData[]>("/planning/repas-semaine");
      return data;
    },
    staleTime: 1000 * 60 * 5,
  });

  const mutation = useMutation({
    mutationFn: () => {
      const items = Object.values(feedbacks);
      return envoyerFeedbackSemaine(items);
    },
    onSuccess: () => setEnvoye(true),
  });

  const setNote = (recetteId: number, note: number) => {
    setFeedbacks((prev) => ({
      ...prev,
      [recetteId]: { ...prev[recetteId], recette_id: recetteId, note, mange: true },
    }));
  };

  const setCommentaire = (recetteId: number, commentaire: string) => {
    setFeedbacks((prev) => ({
      ...prev,
      [recetteId]: { ...prev[recetteId], recette_id: recetteId, note: prev[recetteId]?.note ?? 3, commentaire },
    }));
  };

  const toggleMange = (recetteId: number) => {
    setFeedbacks((prev) => ({
      ...prev,
      [recetteId]: {
        ...prev[recetteId],
        recette_id: recetteId,
        note: prev[recetteId]?.note ?? 3,
        mange: !(prev[recetteId]?.mange ?? true),
      },
    }));
  };

  if (envoye) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <CheckCircle className="h-16 w-16 text-green-500" />
        <h2 className="text-xl font-bold">Merci pour vos retours !</h2>
        <p className="text-muted-foreground text-center">
          Vos feedbacks aident l&apos;IA à améliorer les suggestions de la semaine prochaine.
        </p>
        <Button variant="outline" onClick={() => setEnvoye(false)}>
          Modifier
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Star className="h-6 w-6 text-yellow-500" />
          Qu&apos;avez-vous vraiment mangé ?
        </h1>
        <p className="text-muted-foreground">
          Notez les repas de la semaine pour améliorer les suggestions IA
        </p>
      </div>

      {repasQuery.isLoading ? (
        <div className="flex items-center gap-2 justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin" />
          Chargement des repas...
        </div>
      ) : repasQuery.data && repasQuery.data.length > 0 ? (
        <div className="space-y-4">
          {repasQuery.data.map((repas) => {
            const fb = feedbacks[repas.recette_id];
            const note = fb?.note ?? 0;
            const mange = fb?.mange ?? true;

            return (
              <Card key={`${repas.date_repas}-${repas.recette_id}`}>
                <CardContent className="p-4">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    {/* Info repas */}
                    <div className="flex-1">
                      <p className="font-medium">{repas.recette_nom}</p>
                      <p className="text-xs text-muted-foreground">
                        {repas.date_repas} — {repas.type_repas}
                      </p>
                    </div>

                    {/* Mangé ? */}
                    <Button
                      variant={mange ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleMange(repas.recette_id)}
                    >
                      {mange ? "✓ Mangé" : "✗ Pas mangé"}
                    </Button>

                    {/* Notes étoiles */}
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((n) => (
                        <button
                          key={n}
                          onClick={() => setNote(repas.recette_id, n)}
                          className="p-1"
                        >
                          <Star
                            className={`h-5 w-5 ${
                              n <= note
                                ? "fill-yellow-400 text-yellow-400"
                                : "text-muted-foreground"
                            }`}
                          />
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Commentaire (si noté) */}
                  {note > 0 && (
                    <Textarea
                      placeholder="Un commentaire ? (optionnel)"
                      className="mt-3"
                      rows={2}
                      value={fb?.commentaire ?? ""}
                      onChange={(e) => setCommentaire(repas.recette_id, e.target.value)}
                    />
                  )}
                </CardContent>
              </Card>
            );
          })}

          <Button
            className="w-full"
            size="lg"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || Object.keys(feedbacks).length === 0}
          >
            {mutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Send className="h-4 w-4 mr-2" />
            )}
            Envoyer les feedbacks ({Object.keys(feedbacks).length})
          </Button>
        </div>
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">
              Aucun repas planifié cette semaine. Créez un planning pour donner votre avis !
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
