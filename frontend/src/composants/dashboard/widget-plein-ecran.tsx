// ═════════════════════════════════════════════════════════
// WidgetPleinEcran — F9: Mode plein écran par widget dashboard
// Utilise l'API Fullscreen native (Fullscreen API)
// ═════════════════════════════════════════════════════════
"use client";

import { useCallback, useRef, useState, useEffect } from "react";
import { Maximize2, Minimize2 } from "lucide-react";
import { cn } from "@/bibliotheque/utils";
import { Button } from "@/composants/ui/button";

interface WidgetPleinEcranProps {
  children: React.ReactNode;
  titre?: string;
  className?: string;
}

/**
 * Encapsule un widget dashboard avec un bouton plein-écran.
 * S'appuie sur l'API Fullscreen native (fullscreenchange event).
 * En l'absence de support (navigateur limité), bascule en mode
 * "fixed overlay" couvrant tout l'écran via CSS.
 */
export function WidgetPleinEcran({ children, titre, className }: WidgetPleinEcranProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [estPleinEcran, setEstPleinEcran] = useState(false);

  // Synchroniser l'état avec les événements natifs (ESC, F11, etc.)
  useEffect(() => {
    function handleChange() {
      setEstPleinEcran(!!document.fullscreenElement);
    }
    document.addEventListener("fullscreenchange", handleChange);
    return () => document.removeEventListener("fullscreenchange", handleChange);
  }, []);

  const basculer = useCallback(async () => {
    if (!ref.current) return;
    try {
      if (!document.fullscreenElement) {
        await ref.current.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    } catch {
      // Fallback: Toggle CSS overlay si l'API Fullscreen n'est pas disponible
      setEstPleinEcran((prev) => !prev);
    }
  }, []);

  return (
    <div
      ref={ref}
      className={cn(
        "group relative rounded-xl",
        estPleinEcran && !document.fullscreenElement
          ? "fixed inset-0 z-50 overflow-auto bg-background p-6"
          : "",
        className
      )}
    >
      {/* Bouton plein-écran — affiché au survol */}
      <button
        onClick={basculer}
        aria-label={estPleinEcran ? "Quitter le plein écran" : "Agrandir en plein écran"}
        title={estPleinEcran ? "Quitter le plein écran" : "Plein écran"}
        className={cn(
          "absolute right-2 top-2 z-10 rounded-md p-1.5 text-muted-foreground",
          "opacity-0 transition-opacity group-hover:opacity-100",
          "hover:bg-muted hover:text-foreground",
          "focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        )}
      >
        {estPleinEcran ? (
          <Minimize2 className="h-3.5 w-3.5" />
        ) : (
          <Maximize2 className="h-3.5 w-3.5" />
        )}
      </button>

      {/* Barre de titre affichée uniquement en plein écran */}
      {estPleinEcran && titre ? (
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">{titre}</h2>
          <Button variant="ghost" size="sm" onClick={basculer} className="gap-1.5">
            <Minimize2 className="h-4 w-4" />
            Quitter
          </Button>
        </div>
      ) : null}

      {children}
    </div>
  );
}
