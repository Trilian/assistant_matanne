// ═══════════════════════════════════════════════════════════
// Store Notifications (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";

export interface Notification {
  id: string;
  type: "succes" | "erreur" | "info" | "attention";
  message: string;
  titre?: string;
}

interface EtatNotifications {
  notifications: Notification[];
  ajouter: (notification: Omit<Notification, "id">) => void;
  retirer: (id: string) => void;
  vider: () => void;
}

let compteurId = 0;

export const utiliserStoreNotifications = create<EtatNotifications>((set) => ({
  notifications: [],
  ajouter: (notification) => {
    const id = String(++compteurId);
    set((s) => ({
      notifications: [...s.notifications, { ...notification, id }],
    }));
    // Auto-retrait après 5 secondes
    setTimeout(() => {
      set((s) => ({
        notifications: s.notifications.filter((n) => n.id !== id),
      }));
    }, 5000);
  },
  retirer: (id) =>
    set((s) => ({ notifications: s.notifications.filter((n) => n.id !== id) })),
  vider: () => set({ notifications: [] }),
}));
