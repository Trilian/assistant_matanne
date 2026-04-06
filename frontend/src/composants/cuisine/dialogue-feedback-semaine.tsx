// ═══════════════════════════════════════════════════════════
// Dialog Feedback Semaine — Note les repas pour l'IA
// ═══════════════════════════════════════════════════════════

"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Star, Send, Loader2, CheckCircle } from "lucide-react";
import { Card, CardContent } from "@/composants/ui/card";
import { Button } from "@/composants/ui/button";
import { Textarea } from "@/composants/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/composants/ui/dialog";
import { envoyerFeedbackSemaine, type FeedbackItem } from "@/bibliotheque/api/ia-bridges";
import { clientApi } from "@/bibliotheque/api/client";

interface RepasData {
  id: number;
  type_repas: string;
  recette_nom: string;
  recette_id: number;
  date_repas: string;
}

interface DialogueFeedbackSemaineProps {
  ouvert: boolean;
  onFermer: () => void;
}

export function DialogueFeedbackSemaine({ ouvert, onFermer }: DialogueFeedbackSemaineProps) {
  const [feedbacks, setFeedbacks] = useState<Record<number, FeedbackItem>>({});
  const [envoye, setEnvoye] = useState(false);

  const repasQuery = useQuery({
    queryKey: ["repas-semaine-feedback"],
    queryFn: async () => {
      const { data } = await clientApi.get<RepasData[]>("/planning/repas-semaine");
      return data;
    },
    staleTime: 1000 * 60 * 5,
    enabled: ouvert,
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

  const handleFermer = () => {
    if (envoye) {
      setEnvoye(false);
      setFeedbacks({});
    }
    onFermer();
  };

  return (
    <Dialog open={ouvert} onOpenChange={handleFermer}>
      <DialogContent className="max-w-lg max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Star className="h-5 w-5 text-yellow-500" />
            Qu&apos;avez-vous vraiment mangé ?
          </DialogTitle>
          <DialogDescription>
            Notez les repas pour améliorer les suggestions IA
          </DialogDescription>
        </DialogHeader>

        {envoye ? (
          <div className="flex flex-col items-center justify-center py-8 gap-4">
            <CheckCircle className="h-12 w-12 text-green-500" />
            <p className="font-semibold">Merci pour vos retours !</p>
            <p className="text-sm text-muted-foreground text-center">
              Vos feedbacks aident l&apos;IA à améliorer les suggestions.
            </p>
          </div>
        ) : repasQuery.isLoading ? (
          <div className="flex items-center gap-2 justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin" />
            Chargement des repas...
          </div>
        ) : repasQuery.data && repasQuery.data.length > 0 ? (
          <div className="space-y-3">
            {repasQuery.data.map((repas) => {
              const fb = feedbacks[repas.recette_id];
              const note = fb?.note ?? 0;
              const mange = fb?.mange ?? true;

              return (
                <Card key={`${repas.date_repas}-${repas.recette_id}`}>
                  <CardContent className="p-3">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                      <div className="flex-1">
                        <p className="font-medium text-sm">{repas.recette_nom}</p>
                        <p className="text-xs text-muted-foreground">
                          {repas.date_repas} — {repas.type_repas}
                        </p>
                      </div>
                      <Button
                        variant={mange ? "default" : "outline"}
                        size="sm"
                        onClick={() => toggleMange(repas.recette_id)}
                      >
                        {mange ? "✓ Mangé" : "✗ Pas mangé"}
                      </Button>
                      <div className="flex gap-0.5">
                        {[1, 2, 3, 4, 5].map((n) => (
                          <button key={n} onClick={() => setNote(repas.recette_id, n)} className="p-0.5">
                            <Star
                              className={`h-4 w-4 ${
                                n <= note ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground"
                              }`}
                            />
                          </button>
                        ))}
                      </div>
                    </div>
                    {note > 0 && (
                      <Textarea
                        placeholder="Un commentaire ? (optionnel)"
                        className="mt-2"
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
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending || Object.keys(feedbacks).length === 0}
            >
              {mutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              Envoyer ({Object.keys(feedbacks).length})
            </Button>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-8">
            Aucun repas planifié cette semaine.
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}
