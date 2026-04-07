// ═══════════════════════════════════════════════════════════
// Store Auth — État authentification (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";
import type { Utilisateur } from "@/types/api";

interface EtatAuth {
  utilisateur: Utilisateur | null;
  estConnecte: boolean;
  estChargement: boolean;
  definirUtilisateur: (utilisateur: Utilisateur | null) => void;
  definirChargement: (chargement: boolean) => void;
  reinitialiser: () => void;
}

export const utiliserStoreAuth = create<EtatAuth>((set) => ({
  utilisateur: null,
  estConnecte: false,
  estChargement: false,
  definirUtilisateur: (utilisateur) =>
    set({ utilisateur, estConnecte: !!utilisateur, estChargement: false }),
  definirChargement: (estChargement) => set({ estChargement }),
  reinitialiser: () =>
    set({ utilisateur: null, estConnecte: false, estChargement: false }),
}));
