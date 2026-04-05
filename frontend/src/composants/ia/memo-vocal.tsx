// ═══════════════════════════════════════════════════════════
// Composant Memo Vocal — STT + classification IA (P6)
// ═══════════════════════════════════════════════════════════

"use client";

import { useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { Mic, MicOff, Loader2, ArrowRight, X, Captions, Sparkles } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/composants/ui/card";
import { Badge } from "@/composants/ui/badge";
import { classifierMemoVocal } from "@/bibliotheque/api/ia-avancee";
import type { MemoVocalResponse } from "@/types/ia-avancee";

type ReconnaissanceNavigateur = new () => SpeechRecognition;
type FenetreReconnaissance = Window & {
  SpeechRecognition?: ReconnaissanceNavigateur;
  webkitSpeechRecognition?: ReconnaissanceNavigateur;
};

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

const EXEMPLES_MEMOS = ["Ajoute du lait à la liste", "Note : appeler le plombier", "Prévoir un dîner végétal demain"];

export function MemoVocal() {
  const router = useRouter();
  const [enEcoute, setEnEcoute] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [resultat, setResultat] = useState<MemoVocalResponse | null>(null);
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const supportVocal =
    typeof window !== "undefined" &&
    Boolean((window as FenetreReconnaissance).SpeechRecognition || (window as FenetreReconnaissance).webkitSpeechRecognition);
  const confiancePourcent = resultat ? Math.round(resultat.confiance * 100) : 0;

  const demarrerEcoute = useCallback(() => {
    const fenetre = window as FenetreReconnaissance;
    const SpeechRecognition = fenetre.SpeechRecognition || fenetre.webkitSpeechRecognition;

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
    <Card className="w-full max-w-md overflow-hidden border-sky-200/70 bg-[linear-gradient(135deg,rgba(240,249,255,0.96),rgba(255,255,255,0.92))] shadow-sm dark:border-sky-900/60 dark:bg-[linear-gradient(135deg,rgba(8,19,30,0.96),rgba(9,14,22,0.94))]">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2 text-base">
              <Mic className="h-4 w-4" />
              Mémo vocal
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Capturez une idée à la voix puis laissez l&apos;IA proposer le bon module familial.
            </p>
          </div>
          <Badge variant={supportVocal ? "secondary" : "outline"}>{supportVocal ? "Prêt" : "Limité"}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline">fr-FR</Badge>
          <Badge variant="outline">Capture rapide</Badge>
          <Badge variant="outline">Routage IA</Badge>
        </div>

        <div className="flex justify-center">
          <Button
            size="lg"
            variant={enEcoute ? "destructive" : "default"}
            className="h-20 w-20 rounded-full shadow-lg"
            onClick={enEcoute ? arreterEcoute : demarrerEcoute}
            aria-pressed={enEcoute}
          >
            {enEcoute ? <MicOff className="h-7 w-7 animate-pulse" /> : <Mic className="h-7 w-7" />}
          </Button>
        </div>

        <div className="text-center text-sm text-muted-foreground" role="status" aria-live="polite">
          {enEcoute ? "🎙️ Écoute active — parlez maintenant…" : "Touchez le micro puis dictez une action ou une note."}
        </div>

        <div className="rounded-xl border bg-background/70 p-3 text-sm">
          <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
            <Captions className="h-3.5 w-3.5" />
            Exemples rapides
          </div>
          <div className="flex flex-wrap gap-2">
            {EXEMPLES_MEMOS.map((exemple) => (
              <button
                key={exemple}
                type="button"
                onClick={() => setTranscription(exemple)}
                className="rounded-full border border-dashed px-2.5 py-1 text-xs transition-colors hover:bg-muted"
              >
                {exemple}
              </button>
            ))}
          </div>
        </div>

        {transcription && (
          <div className="rounded-xl border bg-background/80 p-3 text-sm shadow-sm">
            <p className="mb-1 text-xs text-muted-foreground">Transcription détectée</p>
            <p>{transcription}</p>
          </div>
        )}

        {transcription && !resultat && (
          <div className="flex gap-2">
            <Button onClick={classifier} disabled={chargement} className="flex-1" size="sm">
              {chargement ? (
                <>
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                  Classification…
                </>
              ) : (
                <>
                  <Sparkles className="mr-1 h-4 w-4" />
                  Classifier avec l&apos;IA
                </>
              )}
            </Button>
            <Button variant="ghost" size="sm" onClick={reinitialiser}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}

        {resultat && (
          <div className="space-y-3 rounded-xl border bg-background/80 p-3 shadow-sm">
            <div className="flex items-start justify-between gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <Badge>{LABELS_MODULES[resultat.module] ?? resultat.module}</Badge>
                <Badge variant="outline">{resultat.action}</Badge>
              </div>
              <span
                className={`text-xs font-medium ${
                  confiancePourcent >= 80 ? "text-emerald-600" : confiancePourcent >= 60 ? "text-amber-600" : "text-muted-foreground"
                }`}
              >
                Confiance {confiancePourcent}%
              </span>
            </div>
            <p className="text-sm leading-6">{resultat.contenu}</p>
            {resultat.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
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
                  Aller
                  <ArrowRight className="ml-1 h-3 w-3" />
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={reinitialiser}>
                Nouveau
              </Button>
            </div>
          </div>
        )}

        {erreur && <p className="text-center text-sm text-destructive">{erreur}</p>}
      </CardContent>
    </Card>
  );
}
