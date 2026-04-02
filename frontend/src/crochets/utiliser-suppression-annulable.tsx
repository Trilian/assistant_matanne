"use client";

import { useCallback, useEffect, useRef } from "react";
import { toast } from "sonner";

interface SuppressionEnAttente {
  id: string;
  timer: ReturnType<typeof setTimeout>;
}

interface OptionsSuppressionAnnulable {
  ttlMs?: number;
}

export function utiliserSuppressionAnnulable({ ttlMs = 10000 }: OptionsSuppressionAnnulable = {}) {
  const suppressionsRef = useRef<Map<string, SuppressionEnAttente>>(new Map());

  useEffect(() => {
    return () => {
      for (const suppression of suppressionsRef.current.values()) {
        clearTimeout(suppression.timer);
      }
      suppressionsRef.current.clear();
    };
  }, []);

  const planifierSuppression = useCallback(
    (
      cle: string,
      options: {
        libelle: string;
        onConfirmer: () => Promise<void> | void;
        onAnnuler?: () => void;
        onErreur?: () => void;
      }
    ) => {
      const existante = suppressionsRef.current.get(cle);
      if (existante) {
        clearTimeout(existante.timer);
        suppressionsRef.current.delete(cle);
      }

      const timer = setTimeout(async () => {
        suppressionsRef.current.delete(cle);
        try {
          await options.onConfirmer();
        } catch {
          options.onErreur?.();
        }
      }, ttlMs);

      suppressionsRef.current.set(cle, { id: cle, timer });

      toast.success(`${options.libelle} supprimé`, {
        description: `Annulation possible pendant ${Math.round(ttlMs / 1000)} secondes.`,
        duration: ttlMs,
        action: {
          label: "Annuler",
          onClick: () => {
            const suppression = suppressionsRef.current.get(cle);
            if (!suppression) {
              return;
            }
            clearTimeout(suppression.timer);
            suppressionsRef.current.delete(cle);
            options.onAnnuler?.();
            toast.info(`Suppression annulée: ${options.libelle}`);
          },
        },
      });
    },
    [ttlMs]
  );

  return { planifierSuppression };
}