// ═══════════════════════════════════════════════════════════
// Store UI — État interface (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface EtatUI {
  sidebarOuverte: boolean;
  rechercheOuverte: boolean;
  basculerSidebar: () => void;
  definirSidebar: (ouverte: boolean) => void;
  basculerRecherche: () => void;
  definirRecherche: (ouverte: boolean) => void;
}

export const utiliserStoreUI = create<EtatUI>()(
  persist(
    (set) => ({
      sidebarOuverte: true,
      rechercheOuverte: false,
      basculerSidebar: () => set((s) => ({ sidebarOuverte: !s.sidebarOuverte })),
      definirSidebar: (ouverte) => set({ sidebarOuverte: ouverte }),
      basculerRecherche: () => set((s) => ({ rechercheOuverte: !s.rechercheOuverte })),
      definirRecherche: (ouverte) => set({ rechercheOuverte: ouverte }),
    }),
    {
      name: "ui-preferences",
      // On ne persiste que sidebarOuverte — rechercheOuverte reste toujours fermée au démarrage
      partialize: (state) => ({ sidebarOuverte: state.sidebarOuverte }),
    }
  )
);
