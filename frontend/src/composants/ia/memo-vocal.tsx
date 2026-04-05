// ═══════════════════════════════════════════════════════════
// Composant Memo Vocal — STT + classification IA (P6)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Mic, MicOff, Loader2, ArrowRight, X } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { classifierMemoVocal } from "@/bibliotheque/api/ia-avancee";
import type { MemoVocalResponse } from "@/types/ia-avancee";

const LABELS_MODULES: Record<string, string> = {
  courses: "🛒 Courses",
  maison: "🏠 Maison",
  note: "📝 Note",
  routine: "🔄 Routine",
  recette: "🍽️ Recette",
  jardin: "🌱 Jardin",
  famille: "👨‍👩‍👦 Famille",
  rappel: "⏰ Rappel",
};

export function MemoVocal() {
  const router = useRouter();
  const [enEcoute, setEnEcoute] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [resultat, setResultat] = useState<MemoVocalResponse | null>(null);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const demarrerEcoute = useCallback(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setErreur("La reconnaissance vocale n'est pas supportée par votre navigateur.");
      return;
    }

    setErreur(null);
    setResultat(null);
    setTranscription("");

    const recognition = new SpeechRecognition();
    recognition.lang = "fr-FR";
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = Array.from(event.results)
        .map((r) => r[0].transcript)
        .join("");
      setTranscription(transcript);
    };

    recognition.onend = () => {
      setEnEcoute(false);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      setEnEcoute(false);
      if (event.error !== "aborted") {
        setErreur(`Erreur reconnaissance : ${event.error}`);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    setEnEcoute(true);
  }, []);

  const arreterEcoute = useCallback(() => {
    recognitionRef.current?.stop();
    setEnEcoute(false);
  }, []);

  async function classifier() {
    if (!transcription.trim()) return;
    setChargement(true);
    setErreur(null);

    try {
      const res = await classifierMemoVocal(transcription.trim());
      setResultat(res);
    } catch {
      setErreur("Impossible de classifier le mémo. Réessayez.");
    } finally {
      setChargement(false);
    }
  }

  function reinitialiser() {
    setTranscription("");
    setResultat(null);
    setErreur(null);
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Mic className="h-4 w-4" />
          Mémo vocal
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Bouton micro */}
        <div className="flex justify-center">
          <Button
            size="lg"
            variant={enEcoute ? "destructive" : "default"}
            className="rounded-full h-16 w-16"
            onClick={enEcoute ? arreterEcoute : demarrerEcoute}
          >
            {enEcoute ? (
              <MicOff className="h-6 w-6 animate-pulse" />
            ) : (
              <Mic className="h-6 w-6" />
            )}
          </Button>
        </div>

        {enEcoute && (
          <p className="text-center text-sm text-muted-foreground animate-pulse">
            🎙️ Parlez maintenant…
          </p>
        )}

        {/* Transcription */}
        {transcription && (
          <div className="rounded-md bg-muted p-3 text-sm">
            <p className="text-xs text-muted-foreground mb-1">Transcription :</p>
            {transcription}
          </div>
        )}

        {/* Actions post-transcription */}
        {transcription && !resultat && (
          <div className="flex gap-2">
            <Button
              onClick={classifier}
              disabled={chargement}
              className="flex-1"
              size="sm"
            >
              {chargement ? (
                <>
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  Classification…
                </>
              ) : (
                "Classifier avec l'IA"
              )}
            </Button>
            <Button variant="ghost" size="sm" onClick={reinitialiser}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* Résultat */}
        {resultat && (
          <div className="rounded-md border p-3 space-y-2">
            <div className="flex items-center justify-between">
              <Badge>{LABELS_MODULES[resultat.module] ?? resultat.module}</Badge>
              <span className="text-xs text-muted-foreground">
                Confiance : {Math.round(resultat.confiance * 100)}%
              </span>
            </div>
            <p className="text-sm">
              <span className="font-medium">Action :</span> {resultat.action}
            </p>
            <p className="text-sm">{resultat.contenu}</p>
            {resultat.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {resultat.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-[10px]">
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}
            <div className="flex gap-2 pt-1">
              {resultat.destination_url && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => router.push(resultat.destination_url)}
                  className="flex-1"
                >
                  Aller <ArrowRight className="h-3 w-3 ml-1" />
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={reinitialiser}>
                Nouveau
              </Button>
            </div>
          </div>
        )}

        {/* Erreur */}
        {erreur && (
          <p className="text-sm text-destructive text-center">{erreur}</p>
        )}
      </CardContent>
    </Card>
  );
}
