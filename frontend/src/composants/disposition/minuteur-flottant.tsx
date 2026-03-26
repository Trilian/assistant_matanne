"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Timer, X } from "lucide-react";
import { Button } from "@/composants/ui/button";

interface EtatMinuteurGlobal {
  actif: boolean;
  finMs: number;
}

const CLE_MINUTEUR = "outils-minuteur-global";

function lireEtat(): EtatMinuteurGlobal | null {
  if (typeof window === "undefined") return null;
  const brut = window.localStorage.getItem(CLE_MINUTEUR);
  if (!brut) return null;
  try {
    const parsed = JSON.parse(brut) as EtatMinuteurGlobal;
    if (!parsed.actif || !parsed.finMs) return null;
    return parsed;
  } catch {
    return null;
  }
}

function formatMMSS(ms: number): string {
  const totalSec = Math.max(0, Math.floor(ms / 1000));
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function MinuteurFlottant() {
  const [finMs, setFinMs] = useState<number | null>(null);
  const [maintenant, setMaintenant] = useState(Date.now());

  useEffect(() => {
    const sync = () => {
      const etat = lireEtat();
      setFinMs(etat?.finMs ?? null);
    };

    sync();
    const id = window.setInterval(() => {
      setMaintenant(Date.now());
      sync();
    }, 1000);

    const onStorage = () => sync();
    window.addEventListener("storage", onStorage);

    return () => {
      window.clearInterval(id);
      window.removeEventListener("storage", onStorage);
    };
  }, []);

  const restantMs = useMemo(() => {
    if (!finMs) return 0;
    return Math.max(0, finMs - maintenant);
  }, [finMs, maintenant]);

  if (!finMs || restantMs <= 0) return null;

  return (
    <div className="fixed top-14 right-3 z-40">
      <div className="flex items-center gap-2 rounded-full border bg-background/95 px-3 py-1.5 shadow">
        <Timer className="h-4 w-4 text-primary" />
        <span className="text-xs font-medium tabular-nums">{formatMMSS(restantMs)}</span>
        <Link href="/outils/minuteur">
          <Button size="sm" variant="ghost" className="h-6 px-2 text-xs">
            Ouvrir
          </Button>
        </Link>
        <Button
          size="icon"
          variant="ghost"
          className="h-6 w-6"
          onClick={() => {
            window.localStorage.removeItem(CLE_MINUTEUR);
            setFinMs(null);
          }}
          aria-label="Fermer le minuteur flottant"
        >
          <X className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}
