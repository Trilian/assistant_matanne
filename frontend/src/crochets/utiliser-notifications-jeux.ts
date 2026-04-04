"use client";

import { useEffect, useCallback } from "react";
import { toast } from "sonner";

/**
 * Hook pour gérer les notifications Web Push liées aux jeux.
 * 
 * Écoute les événements service worker et affiche les toasts
 * pour les résultats de paris et tirages loto.
 */
export function useNotificationsJeux() {
  const handleNotification = useCallback((event: MessageEvent) => {
    if (event.data?.type === "NOTIFICATION_RECEIVED") {
      const { notification } = event.data;

      // Déterminer le type de notification
      if (notification.notification_type === "jeux_pari_gagne") {
        toast.success(notification.title, {
          description: notification.body,
          action: {
            label: "Voir le bilan",
            onClick: () => {
              window.location.href = notification.url || "/?module=jeux.paris";
            },
          },
          duration: 8000,
        });
      } else if (notification.notification_type === "jeux_pari_perdu") {
        toast.error(notification.title, {
          description: notification.body,
          action: {
            label: "Voir l'analyse",
            onClick: () => {
              window.location.href = notification.url || "/?module=jeux.performance";
            },
          },
          duration: 6000,
        });
      } else if (
        notification.notification_type === "jeux_loto_gain" ||
        notification.notification_type === "jeux_loto_resultat"
      ) {
        const isGain = notification.notification_type === "jeux_loto_gain";
        toast(notification.title, {
          description: notification.body,
          action: {
            label: "Voir les détails",
            onClick: () => {
              window.location.href = notification.url || "/?module=jeux.loto";
            },
          },
          duration: isGain ? 10000 : 5000,
          className: isGain ? "border-l-4 border-emerald-500" : "",
        });
      } else if (notification.notification_type === "jeux_serie_defaites") {
        toast.warning(notification.title, {
          description: notification.body,
          action: {
            label: "Voir le bilan",
            onClick: () => {
              window.location.href = notification.url || "/?module=jeux.responsable";
            },
          },
          duration: 10000,
        });
      }
    }
  }, []);

  useEffect(() => {
    if ("serviceWorker" in navigator) {
      // Écouter les messages du service worker
      navigator.serviceWorker.addEventListener("message", handleNotification);

      return () => {
        navigator.serviceWorker.removeEventListener("message", handleNotification);
      };
    }
  }, [handleNotification]);
}

/**
 * Demander la permission pour les notifications jeux
 */
export async function demanderPermissionNotificationsJeux(): Promise<boolean> {
  if (!("Notification" in window)) {
    toast.error("Les notifications ne sont pas supportées par ce navigateur");
    return false;
  }

  if (Notification.permission === "granted") {
    return true;
  }

  if (Notification.permission === "denied") {
    toast.error("Les notifications ont été bloquées. Modifiez les paramètres du navigateur.");
    return false;
  }

  const permission = await Notification.requestPermission();
  if (permission === "granted") {
    toast.success("Notifications activées pour les résultats de jeux ! 🎰");
    return true;
  } else {
    toast.error("Permission refusée");
    return false;
  }
}
