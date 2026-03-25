"use client";

import { useState, useEffect, useCallback } from "react";
import { Download, X } from "lucide-react";
import { Button } from "@/composants/ui/button";

const CLE_DISMISS = "pwa-install-dismissed";
const CLE_VISITES = "pwa-visit-count";
const SEUIL_VISITES = 3;
const DELAI_AFFICHAGE_MS = 5 * 60 * 1000; // 5 min

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

/**
 * Bannière d'installation PWA — s'affiche après 3 visites ou 5 minutes,
 * sauf si l'utilisateur l'a déjà fermée ou si l'app est déjà installée.
 */
export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] =
    useState<BeforeInstallPromptEvent | null>(null);
  const [afficher, setAfficher] = useState(false);

  const verifierConditions = useCallback(
    (prompt: BeforeInstallPromptEvent | null) => {
      if (!prompt) return false;

      // Déjà fermé par l'utilisateur
      if (localStorage.getItem(CLE_DISMISS) === "true") return false;

      // Déjà installé (standalone)
      if (window.matchMedia("(display-mode: standalone)").matches) return false;

      // Vérifier nombre de visites
      const visites = parseInt(localStorage.getItem(CLE_VISITES) || "0", 10);
      return visites >= SEUIL_VISITES;
    },
    []
  );

  useEffect(() => {
    // Incrémenter compteur de visites
    const visites = parseInt(localStorage.getItem(CLE_VISITES) || "0", 10) + 1;
    localStorage.setItem(CLE_VISITES, String(visites));

    const gererPrompt = (e: Event) => {
      e.preventDefault();
      const prompt = e as BeforeInstallPromptEvent;
      setDeferredPrompt(prompt);

      // Afficher immédiatement si seuil de visites atteint
      if (verifierConditions(prompt)) {
        setAfficher(true);
        return;
      }

      // Sinon attendre le délai de 5 min
      if (
        localStorage.getItem(CLE_DISMISS) !== "true" &&
        !window.matchMedia("(display-mode: standalone)").matches
      ) {
        const timer = setTimeout(() => {
          setAfficher(true);
        }, DELAI_AFFICHAGE_MS);
        return () => clearTimeout(timer);
      }
    };

    window.addEventListener("beforeinstallprompt", gererPrompt);

    return () => {
      window.removeEventListener("beforeinstallprompt", gererPrompt);
    };
  }, [verifierConditions]);

  const installer = async () => {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setAfficher(false);
    }
    setDeferredPrompt(null);
  };

  const fermer = () => {
    setAfficher(false);
    localStorage.setItem(CLE_DISMISS, "true");
  };

  if (!afficher) return null;

  return (
    <div className="fixed bottom-20 md:bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-in slide-in-from-bottom-4 duration-300">
      <div className="bg-card border rounded-lg shadow-lg p-4 flex items-start gap-3">
        <div className="flex-shrink-0 bg-primary/10 rounded-full p-2">
          <Download className="h-5 w-5 text-primary" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm">Installer Assistant Matanne</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            Accès rapide depuis votre écran d&apos;accueil, même hors ligne.
          </p>

          <div className="flex gap-2 mt-3">
            <Button size="sm" onClick={installer}>
              Installer
            </Button>
            <Button size="sm" variant="ghost" onClick={fermer}>
              Plus tard
            </Button>
          </div>
        </div>

        <button
          onClick={fermer}
          className="flex-shrink-0 text-muted-foreground hover:text-foreground"
          aria-label="Fermer la bannière d'installation"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
