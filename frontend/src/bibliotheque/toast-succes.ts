// ═══════════════════════════════════════════════════════════
// toast-succes — F11: Toast success avec confetti
// Combine sonner toast + lancerConfettis pour célébrer
// les actions positives (ajout recette, repas validé, etc.)
// ═══════════════════════════════════════════════════════════

import { toast } from "sonner";
import { lancerConfettis } from "@/bibliotheque/confettis";

interface OptionsToastSucces {
  /** Titre principal du toast */
  titre: string;
  /** Description optionnelle sous le titre */
  description?: string;
  /** Nombre de particules confetti (défaut: 28) */
  particules?: number;
  /** Durée du toast en ms (défaut: 4000) */
  duree?: number;
  /** Désactiver le confetti (ex: actions mineures) */
  sansConfetti?: boolean;
}

/**
 * Affiche un toast success avec confettis pour les actions positives.
 *
 * @example
 * toastSucces({ titre: "Recette ajoutée !", description: "Bœuf bourguignon ajouté à vos favoris." });
 * toastSucces({ titre: "Budget atteint 🎉", particules: 50 });
 * toastSucces({ titre: "Sauvegardé", sansConfetti: true });
 */
export function toastSucces({
  titre,
  description,
  particules = 28,
  duree = 4000,
  sansConfetti = false,
}: OptionsToastSucces): void {
  toast.success(titre, {
    description,
    duration: duree,
  });

  if (!sansConfetti) {
    // Petit délai pour que le toast soit affiché avant les confettis
    setTimeout(() => lancerConfettis({ particules }), 80);
  }
}

/**
 * Version légère : toast info sans confetti.
 * Alias pratique pour ne pas avoir à importer sonner directement.
 */
export function toastInfo(titre: string, description?: string): void {
  toast.info(titre, { description });
}

/**
 * Toast d'erreur standardisé.
 */
export function toastErreur(titre: string, description?: string): void {
  toast.error(titre, { description });
}
