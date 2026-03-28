"use client";

import { useState } from "react";
import { Sparkles, Volume2, X } from "lucide-react";
import { BoutonVocal } from "@/composants/ui/bouton-vocal";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { clientApi } from "@/bibliotheque/api/client";

type ReponseCommande = {
  action: string;
  message: string;
};

export function FabAssistantVocal() {
  const [ouvert, setOuvert] = useState(false);
  const [chargement, setChargement] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [reponse, setReponse] = useState<ReponseCommande | null>(null);

  async function executerCommande(texte: string) {
    setTranscription(texte);
    setChargement(true);
    try {
      const { data } = await clientApi.post<ReponseCommande>("/assistant/commande-vocale", {
        texte,
      });
      setReponse(data);
    } catch {
      setReponse({
        action: "erreur",
        message: "Impossible d'exécuter la commande vocale pour le moment.",
      });
    } finally {
      setChargement(false);
    }
  }

  return (
    <div className="fixed bottom-[10rem] right-4 md:bottom-24 z-40 flex flex-col items-end gap-2">
      {ouvert && (
        <Card className="w-80 shadow-xl border animate-in slide-in-from-bottom-4">
          <CardHeader className="pb-2 flex-row items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Volume2 className="h-4 w-4" />
              Assistant vocal
            </CardTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => setOuvert(false)}
              aria-label="Fermer l'assistant vocal"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          </CardHeader>
          <CardContent className="space-y-3 pb-3">
            <p className="text-xs text-muted-foreground">
              Exemples : « Ajoute du lait à la liste », « Jules pèse 11,4 kg », « Quel est mon planning de demain ? »
            </p>
            <BoutonVocal
              onResultat={executerCommande}
              placeholder="Dicter une commande"
              className="w-full justify-center"
              variante="outline"
              taille="default"
            />
            {chargement && <p className="text-sm text-muted-foreground">Analyse en cours...</p>}
            {transcription && (
              <div className="rounded-md bg-muted p-2 text-sm">
                <p className="text-xs text-muted-foreground mb-1">Transcription</p>
                <p>{transcription}</p>
              </div>
            )}
            {reponse && (
              <div className="rounded-md border p-2 text-sm">
                <p className="text-xs text-muted-foreground mb-1">Réponse</p>
                <p>{reponse.message}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Button
        size="icon"
        className="h-12 w-12 rounded-full shadow-lg bg-emerald-600 hover:bg-emerald-700 text-white"
        onClick={() => setOuvert((etat) => !etat)}
        aria-label={ouvert ? "Fermer l'assistant vocal" : "Ouvrir l'assistant vocal"}
      >
        {ouvert ? <X className="h-5 w-5" /> : <Sparkles className="h-5 w-5" />}
      </Button>
    </div>
  );
}