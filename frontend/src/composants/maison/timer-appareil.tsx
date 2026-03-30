// ═══════════════════════════════════════════════════════════
// TimerAppareil — Compte à rebours pour un appareil ménager
// ═══════════════════════════════════════════════════════════

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { utiliserStoreMaison } from "@/magasins/store-maison";
import { Button } from "@/composants/ui/button";

interface TimerAppareilProps {
  appareil: string;
  dureeMin: number;
  actionPost?: string;
  onTermine?: () => void;
  className?: string;
}

function formaterTemps(secondesRestantes: number): string {
  const h = Math.floor(secondesRestantes / 3600);
  const m = Math.floor((secondesRestantes % 3600) / 60);
  const s = secondesRestantes % 60;
  if (h > 0) {
    return `${h}h${m.toString().padStart(2, "0")}min`;
  }
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function TimerAppareil({
  appareil,
  dureeMin,
  actionPost = "",
  onTermine,
  className,
}: TimerAppareilProps) {
  const { timers, lancerTimer, arreterTimer, marquerTimerTermine } =
    utiliserStoreMaison();
  const timer = timers[appareil];

  const [secondesRestantes, setSecondesRestantes] = useState<number | null>(
    null
  );
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Calculer secondes restantes depuis le timer en cours
  const calculerRestant = useCallback(() => {
    if (!timer || timer.termine) return null;
    const ecouleeMs = Date.now() - timer.debutMs;
    const restantMs = timer.dureeTotalMs - ecouleeMs;
    return Math.max(0, Math.floor(restantMs / 1000));
  }, [timer]);

  useEffect(() => {
    if (!timer || timer.termine) {
      setSecondesRestantes(null);
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    const restant = calculerRestant();
    setSecondesRestantes(restant);

    intervalRef.current = setInterval(() => {
      const r = calculerRestant();
      if (r !== null && r <= 0) {
        // Timer terminé
        marquerTimerTermine(appareil);
        if (intervalRef.current) clearInterval(intervalRef.current);
        setSecondesRestantes(0);
        onTermine?.();
        // Notification sonore simple
        try {
          const ctx = new AudioContext();
          const osc = ctx.createOscillator();
          osc.connect(ctx.destination);
          osc.frequency.setValueAtTime(880, ctx.currentTime);
          osc.start();
          osc.stop(ctx.currentTime + 0.5);
        } catch {
          // Pas de contexte audio disponible
        }
      } else {
        setSecondesRestantes(r);
      }
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [timer, timer?.debutMs, timer?.termine, calculerRestant, marquerTimerTermine, appareil, onTermine]);

  const estActif = !!timer && !timer.termine && secondesRestantes !== null;
  const estTermine = timer?.termine === true;

  const handleDemarrer = () => {
    lancerTimer(appareil, dureeMin, actionPost);
  };

  const handleAnnuler = () => {
    arreterTimer(appareil);
    setSecondesRestantes(null);
  };

  const pourcentage =
    estActif && secondesRestantes !== null
      ? Math.round(
          ((timer.dureeTotalMs / 1000 - secondesRestantes) /
            (timer.dureeTotalMs / 1000)) *
            100
        )
      : 0;

  return (
    <div className={`flex items-center gap-3 ${className ?? ""}`}>
      {/* État : pas encore démarré */}
      {!estActif && !estTermine && (
        <Button size="sm" variant="outline" onClick={handleDemarrer}>
          ▶ {dureeMin} min
        </Button>
      )}

      {/* État : en cours */}
      {estActif && secondesRestantes !== null && (
        <div className="flex items-center gap-2">
          {/* Barre de progression circulaire simple */}
          <div className="relative w-10 h-10">
            <svg className="w-10 h-10 -rotate-90" viewBox="0 0 36 36">
              <circle
                cx="18"
                cy="18"
                r="15"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="text-muted-foreground/20"
              />
              <circle
                cx="18"
                cy="18"
                r="15"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeDasharray={`${pourcentage * 0.942} 94.2`}
                className="text-primary transition-all"
              />
            </svg>
            <span className="absolute inset-0 flex items-center justify-center text-[9px] font-mono font-bold">
              {Math.ceil(secondesRestantes / 60)}m
            </span>
          </div>
          <span className="font-mono text-sm font-bold tabular-nums">
            {formaterTemps(secondesRestantes)}
          </span>
          <Button size="sm" variant="ghost" onClick={handleAnnuler} className="text-muted-foreground h-7 px-2">
            ✕
          </Button>
        </div>
      )}

      {/* État : terminé */}
      {estTermine && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-green-600 font-medium">
            🔔 {appareil} terminé
          </span>
          {actionPost && (
            <span className="text-xs text-muted-foreground">{actionPost}</span>
          )}
          <Button size="sm" variant="ghost" onClick={handleAnnuler} className="text-muted-foreground h-7 px-2">
            ✕
          </Button>
        </div>
      )}
    </div>
  );
}
