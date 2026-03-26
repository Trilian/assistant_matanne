// ═══════════════════════════════════════════════════════════
// Store UI — État interface (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface EtatUI {
  sidebarOuverte: boolean;
  rechercheOuverte: boolean;
  /** Titre dynamique pour le fil d'ariane (ex : nom d'une recette sur /recettes/42) */
  titrePage: string | null;
  basculerSidebar: () => void;
  definirSidebar: (ouverte: boolean) => void;
  basculerRecherche: () => void;
  definirRecherche: (ouverte: boolean) => void;
  definirTitrePage: (titre: string | null) => void;
}

export const utiliserStoreUI = create<EtatUI>()(
  persist(
    (set) => ({
      sidebarOuverte: true,
      rechercheOuverte: false,
      titrePage: null,
      basculerSidebar: () => set((s) => ({ sidebarOuverte: !s.sidebarOuverte })),
      definirSidebar: (ouverte) => set({ sidebarOuverte: ouverte }),
      basculerRecherche: () => set((s) => ({ rechercheOuverte: !s.rechercheOuverte })),
      definirRecherche: (ouverte) => set({ rechercheOuverte: ouverte }),
      definirTitrePage: (titre) => set({ titrePage: titre }),
    }),
    {
      name: "ui-preferences",
      // On ne persiste que sidebarOuverte — rechercheOuverte reste toujours fermée au démarrage
      partialize: (state) => ({ sidebarOuverte: state.sidebarOuverte }),
    }
  )
);
