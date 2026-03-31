"use client";

import { useCallback, useMemo, useState } from "react";

interface OptionsSynthese {
  lang?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
}

export function utiliserSyntheseVocale(options: OptionsSynthese = {}) {
  const [enLecture, setEnLecture] = useState(false);

  const estSupporte = useMemo(
    () => typeof window !== "undefined" && "speechSynthesis" in window,
    []
  );

  const lire = useCallback(
    (texte: string) => {
      if (!estSupporte || !texte.trim()) {
        return;
      }

      const utterance = new SpeechSynthesisUtterance(texte);
      utterance.lang = options.lang ?? "fr-FR";
      utterance.rate = options.rate ?? 1;
      utterance.pitch = options.pitch ?? 1;
      utterance.volume = options.volume ?? 1;

      utterance.onstart = () => setEnLecture(true);
      utterance.onend = () => setEnLecture(false);
      utterance.onerror = () => setEnLecture(false);

      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    },
    [estSupporte, options.lang, options.pitch, options.rate, options.volume]
  );

  const arreter = useCallback(() => {
    if (!estSupporte) {
      return;
    }
    window.speechSynthesis.cancel();
    setEnLecture(false);
  }, [estSupporte]);

  return {
    estSupporte,
    enLecture,
    lire,
    arreter,
  };
}
