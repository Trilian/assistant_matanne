// ═══════════════════════════════════════════════════════════
// Store Maison — Timers d'appareils et état ménage (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface TimerAppareil {
  appareil: string;
  debutMs: number;
  dureeTotalMs: number;
  actionPost: string;
  termine: boolean;
}

interface EtatMaison {
  // Timers appareils (lave-linge, lave-vaisselle, etc.)
  timers: Record<string, TimerAppareil>;
  // Tâches du jour cochées (persisté localement)
  tachesTerminees: string[];

  // Actions timers
  lancerTimer: (appareil: string, dureeMin: number, actionPost: string) => void;
  arreterTimer: (appareil: string) => void;
  marquerTimerTermine: (appareil: string) => void;
  timersActifs: () => TimerAppareil[];

  // Actions tâches
  basculerTache: (id: string) => void;
  reinitialiserTachesJour: () => void;
}

export const utiliserStoreMaison = create<EtatMaison>()(
  persist(
    (set, get) => ({
      timers: {},
      tachesTerminees: [],

      lancerTimer: (appareil, dureeMin, actionPost) =>
        set((state) => ({
          timers: {
            ...state.timers,
            [appareil]: {
              appareil,
              debutMs: Date.now(),
              dureeTotalMs: dureeMin * 60 * 1000,
              actionPost,
              termine: false,
            },
          },
        })),

      arreterTimer: (appareil) =>
        set((state) => {
          const timers = { ...state.timers };
          delete timers[appareil];
          return { timers };
        }),

      marquerTimerTermine: (appareil) =>
        set((state) => ({
          timers: {
            ...state.timers,
            [appareil]: { ...state.timers[appareil], termine: true },
          },
        })),

      timersActifs: () =>
        Object.values(get().timers).filter((t) => !t.termine),

      basculerTache: (id) =>
        set((state) => ({
          tachesTerminees: state.tachesTerminees.includes(id)
            ? state.tachesTerminees.filter((t) => t !== id)
            : [...state.tachesTerminees, id],
        })),

      reinitialiserTachesJour: () => set({ tachesTerminees: [] }),
    }),
    {
      name: "maison-store",
      // Ne persister que les tâches terminées (les timers sont réinitialisés au rechargement)
      partialize: (state) => ({ tachesTerminees: state.tachesTerminees }),
    }
  )
);
