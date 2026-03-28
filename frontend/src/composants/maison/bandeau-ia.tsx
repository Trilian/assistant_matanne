// ─── BandeauIA ─────────────────────────────────────────────
// Bandeau de conseil IA contextuel pour chaque section Maison.
// Se rétracte/déploie via un bouton. Fetch le conseil si non mis en cache.
"use client";

import { useState } from "react";
import { Sparkles, ChevronDown, ChevronUp, RefreshCw } from "lucide-react";
import { Button } from "@/composants/ui/button";
import { Skeleton } from "@/composants/ui/skeleton";
import { utiliserRequete } from "@/crochets/utiliser-api";
import { obtenirConseilIA } from "@/bibliotheque/api/maison";

interface BandeauIAProps {
  /** Nom de la section (ex: "travaux", "finances", "provisions", "jardin"…) */
  section: string;
}

export function BandeauIA({ section }: BandeauIAProps) {
  const [deploye, setDeploy] = useState(false);
  const [clefRafraichi, setClefRafraichi] = useState(0);

  const { data, isFetching, refetch } = utiliserRequete(
    ["maison", "conseil-ia", section, String(clefRafraichi)],
    () => obtenirConseilIA(section),
    {
      // Ne charge que si le bandeau est ouvert
      enabled: deploye,
      staleTime: 5 * 60 * 1000, // 5 min
    }
  );

  const rafraichir = () => {
    setClefRafraichi((k) => k + 1);
    refetch();
  };

  return (
    <div className="rounded-lg border bg-gradient-to-r from-violet-50 to-indigo-50 dark:from-violet-950/30 dark:to-indigo-950/30 border-violet-200 dark:border-violet-800">
      {/* En-tête */}
      <button
        type="button"
        className="w-full flex items-center gap-2 p-3 text-left"
        onClick={() => setDeploy((d) => !d)}
      >
        <Sparkles className="h-4 w-4 text-violet-500 shrink-0" />
        <span className="text-sm font-medium text-violet-700 dark:text-violet-300 flex-1">
          Assistant IA — {section}
        </span>
        {deploye ? (
          <ChevronUp className="h-4 w-4 text-violet-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-violet-400" />
        )}
      </button>

      {/* Contenu */}
      {deploye && (
        <div className="px-3 pb-3 space-y-2">
          {isFetching ? (
            <div className="space-y-1.5">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-4/5" />
              <Skeleton className="h-3 w-3/5" />
            </div>
          ) : data ? (
            <>
              {Array.isArray(data.conseils) ? (
                <ul className="space-y-1.5">
                  {data.conseils.map((c: string, i: number) => (
                    <li key={i} className="text-sm text-muted-foreground flex gap-1.5">
                      <span className="text-violet-400 shrink-0">•</span>
                      {c}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">{data.conseil ?? data.message ?? "Aucun conseil"}</p>
              )}
              <div className="flex justify-end">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 gap-1.5 text-violet-600 hover:text-violet-700"
                  onClick={rafraichir}
                  disabled={isFetching}
                >
                  <RefreshCw className={`h-3 w-3 ${isFetching ? "animate-spin" : ""}`} />
                  Rafraîchir
                </Button>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground italic">Cliquez pour charger les conseils…</p>
          )}
        </div>
      )}
    </div>
  );
}
