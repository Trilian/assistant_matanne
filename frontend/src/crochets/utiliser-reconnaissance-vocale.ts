"use client";

import { useState, useRef, useCallback, useEffect } from "react";

interface OptionsReconnaissanceVocale {
  langue?: string;
  continu?: boolean;
  resultatsInterimaires?: boolean;
  onResultat?: (texte: string) => void;
}

interface RetourReconnaissanceVocale {
  transcription: string;
  enEcoute: boolean;
  demarrerEcoute: () => void;
  arreterEcoute: () => void;
  estSupporte: boolean;
  erreur: string | null;
  reinitialiser: () => void;
}

export function utiliserReconnaissanceVocale(
  options: OptionsReconnaissanceVocale = {}
): RetourReconnaissanceVocale {
  const {
    langue = "fr-FR",
    continu = true,
    resultatsInterimaires = true,
    onResultat,
  } = options;

  const [transcription, setTranscription] = useState("");
  const [enEcoute, setEnEcoute] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  const reconnaissanceRef = useRef<SpeechRecognition | null>(null);
  const onResultatRef = useRef(onResultat);
  onResultatRef.current = onResultat;

  const estSupporte =
    typeof window !== "undefined" &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  const demarrerEcoute = useCallback(() => {
    if (!estSupporte) {
      setErreur("La reconnaissance vocale n'est pas supportée par ce navigateur");
      return;
    }

    setErreur(null);

    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const reconnaissance = new SpeechRecognitionAPI();

    reconnaissance.lang = langue;
    reconnaissance.continuous = continu;
    reconnaissance.interimResults = resultatsInterimaires;

    reconnaissance.onresult = (event: SpeechRecognitionEvent) => {
      let texteInterimaire = "";
      let texteFinal = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const resultat = event.results[i];
        if (resultat.isFinal) {
          texteFinal += resultat[0].transcript;
        } else {
          texteInterimaire += resultat[0].transcript;
        }
      }

      if (texteFinal) {
        setTranscription((prev) => {
          const nouveau = prev ? `${prev} ${texteFinal}` : texteFinal;
          onResultatRef.current?.(texteFinal.trim());
          return nouveau;
        });
      } else if (texteInterimaire) {
        // On ne stocke pas les résultats intérimaires dans la transcription finale
        // mais on pourrait les afficher via un état séparé si nécessaire
      }
    };

    reconnaissance.onerror = (event: SpeechRecognitionErrorEvent) => {
      const messages: Record<string, string> = {
        "not-allowed": "Permission micro refusée. Autorisez l'accès au microphone.",
        "no-speech": "Aucune parole détectée.",
        "audio-capture": "Aucun micro détecté.",
        network: "Erreur réseau pour la reconnaissance vocale.",
        aborted: "Reconnaissance vocale interrompue.",
      };
      setErreur(messages[event.error] || `Erreur: ${event.error}`);
      setEnEcoute(false);
    };

    reconnaissance.onend = () => {
      setEnEcoute(false);
    };

    reconnaissanceRef.current = reconnaissance;
    reconnaissance.start();
    setEnEcoute(true);
  }, [estSupporte, langue, continu, resultatsInterimaires]);

  const arreterEcoute = useCallback(() => {
    reconnaissanceRef.current?.stop();
    setEnEcoute(false);
  }, []);

  const reinitialiser = useCallback(() => {
    arreterEcoute();
    setTranscription("");
    setErreur(null);
  }, [arreterEcoute]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      reconnaissanceRef.current?.stop();
    };
  }, []);

  return {
    transcription,
    enEcoute,
    demarrerEcoute,
    arreterEcoute,
    estSupporte,
    erreur,
    reinitialiser,
  };
}
