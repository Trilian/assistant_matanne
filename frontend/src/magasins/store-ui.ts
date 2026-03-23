// ═══════════════════════════════════════════════════════════
// Store UI — État interface (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";

interface EtatUI {
  sidebarOuverte: boolean;
  rechercheOuverte: boolean;
  basculerSidebar: () => void;
  definirSidebar: (ouverte: boolean) => void;
  basculerRecherche: () => void;
  definirRecherche: (ouverte: boolean) => void;
}

export const utiliserStoreUI = create<EtatUI>((set) => ({
  sidebarOuverte: true,
  rechercheOuverte: false,
  basculerSidebar: () => set((s) => ({ sidebarOuverte: !s.sidebarOuverte })),
  definirSidebar: (ouverte) => set({ sidebarOuverte: ouverte }),
  basculerRecherche: () => set((s) => ({ rechercheOuverte: !s.rechercheOuverte })),
  definirRecherche: (ouverte) => set({ rechercheOuverte: ouverte }),
}));
