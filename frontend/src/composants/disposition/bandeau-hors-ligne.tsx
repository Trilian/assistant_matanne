"use client";

import { useState, useEffect } from "react";
import { WifiOff, RefreshCw, CheckCircle2 } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { utiliserHorsLigne } from "@/crochets/utiliser-hors-ligne";

export function BandeauHorsLigne() {
  const { estHorsLigne, nbEnAttente, forcerSync } = utiliserHorsLigne();
  const [masquerSync, setMasquerSync] = useState(false);

  // Auto-masquer "Synchronisation rétablie" après 4 s pour éviter le bandeau bloqué
  useEffect(() => {
    if (!estHorsLigne && nbEnAttente > 0) {
      setMasquerSync(false);
      const timer = setTimeout(() => setMasquerSync(true), 4000);
      return () => clearTimeout(timer);
    }
    setMasquerSync(false);
  }, [estHorsLigne, nbEnAttente]);

  if (estHorsLigne) {
    return (
      <div className="border-b bg-amber-50/90 px-4 py-2 text-amber-900 dark:bg-amber-900/20 dark:text-amber-100">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-3 text-sm">
          <div className="flex items-center gap-2">
            <WifiOff className="h-4 w-4" />
            <span>
              Mode hors-ligne actif
              {nbEnAttente > 0 ? ` - ${nbEnAttente} action(s) en attente de sync` : ""}
            </span>
          </div>
          <Button
            size="sm"
            variant="outline"
            className="h-7 border-amber-400 bg-transparent text-xs"
            onClick={() => {
              void forcerSync();
            }}
          >
            <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
            Réessayer la sync
          </Button>
        </div>
      </div>
    );
  }

  if (nbEnAttente > 0 && !masquerSync) {
    return (
      <div className="border-b bg-emerald-50/90 px-4 py-2 text-emerald-900 dark:bg-emerald-900/20 dark:text-emerald-100">
        <div className="mx-auto flex w-full max-w-7xl items-center gap-2 text-sm">
          <CheckCircle2 className="h-4 w-4" />
          Synchronisation rétablie.
        </div>
      </div>
    );
  }

  return null;
}