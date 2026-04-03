// ═══════════════════════════════════════════════════════════
// Store Notifications (Zustand)
// ═══════════════════════════════════════════════════════════

import { create } from "zustand";

const CLES_PREFS_NOTIFICATIONS = "notifications:preferences";

export interface Notification {
  id: string;
  type: "succes" | "erreur" | "info" | "attention";
  message: string;
  titre?: string;
}

interface EtatNotifications {
  notifications: Notification[];
  autoDismissMs: number;
  conserverErreurs: boolean;
  ajouter: (notification: Omit<Notification, "id">) => void;
  retirer: (id: string) => void;
  vider: () => void;
  definirPreferences: (prefs: Partial<Pick<EtatNotifications, "autoDismissMs" | "conserverErreurs">>) => void;
}

let compteurId = 0;

function chargerPrefs() {
  if (typeof window === "undefined") {
    return { autoDismissMs: 5000, conserverErreurs: true };
  }

  try {
    const brut = window.localStorage.getItem(CLES_PREFS_NOTIFICATIONS);
    if (!brut) {
      return { autoDismissMs: 5000, conserverErreurs: true };
    }
    const parsed = JSON.parse(brut) as {
      autoDismissMs?: unknown;
      conserverErreurs?: unknown;
    };
    const autoDismissMs =
      typeof parsed.autoDismissMs === "number" && parsed.autoDismissMs >= 2000 && parsed.autoDismissMs <= 60000
        ? Math.round(parsed.autoDismissMs)
        : 5000;
    const conserverErreurs =
      typeof parsed.conserverErreurs === "boolean" ? parsed.conserverErreurs : true;
    return { autoDismissMs, conserverErreurs };
  } catch {
    return { autoDismissMs: 5000, conserverErreurs: true };
  }
}

const prefsParDefaut = chargerPrefs();

export const utiliserStoreNotifications = create<EtatNotifications>((set) => ({
  notifications: [],
  autoDismissMs: prefsParDefaut.autoDismissMs,
  conserverErreurs: prefsParDefaut.conserverErreurs,
  ajouter: (notification) => {
    const id = String(++compteurId);
    set((s) => ({
      notifications: [...s.notifications, { ...notification, id }],
    }));

    const { autoDismissMs, conserverErreurs } = utiliserStoreNotifications.getState();
    const doitRester = notification.type === "erreur" && conserverErreurs;
    if (!doitRester) {
      setTimeout(() => {
        set((s) => ({
          notifications: s.notifications.filter((n) => n.id !== id),
        }));
      }, autoDismissMs);
    }
  },
  retirer: (id) =>
    set((s) => ({ notifications: s.notifications.filter((n) => n.id !== id) })),
  vider: () => set({ notifications: [] }),
  definirPreferences: (prefs) =>
    set((s) => {
      const prochain = {
        autoDismissMs:
          typeof prefs.autoDismissMs === "number" && prefs.autoDismissMs >= 2000 && prefs.autoDismissMs <= 60000
            ? Math.round(prefs.autoDismissMs)
            : s.autoDismissMs,
        conserverErreurs:
          typeof prefs.conserverErreurs === "boolean"
            ? prefs.conserverErreurs
            : s.conserverErreurs,
      };

      if (typeof window !== "undefined") {
        window.localStorage.setItem(CLES_PREFS_NOTIFICATIONS, JSON.stringify(prochain));
      }

      return prochain;
    }),
}));

export function useNotifications() {
  const ajouter = utiliserStoreNotifications((state) => state.ajouter);

  const ajouter_notification = (message: string, type: Notification["type"] = "info") => {
    ajouter({
      message,
      type,
    });
  };

  return { ajouter_notification };
}
