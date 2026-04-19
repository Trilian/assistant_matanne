import { useMemo } from "react";
import { utiliserWebSocket } from "@/crochets/utiliser-websocket";

type UtilisateurPlanning = {
  id?: string | number | null;
  email?: string | null;
  nom?: string | null;
} | null;

type InvaliderFn = (cles: string[]) => void;

export function utiliserPresencePlanning(
  utilisateur: UtilisateurPlanning,
  dateDebut: string,
  invalider: InvaliderFn
) {
  const identifiantPresencePlanning = String(utilisateur?.id ?? utilisateur?.email ?? "");
  const nomPresencePlanning = String(utilisateur?.nom ?? "Membre du foyer");

  const urlWsPlanning = useMemo(() => {
    const baseWsPlanning = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/^http/, "ws");
    const salonPlanningId = Number(dateDebut.replaceAll("-", ""));
    if (!identifiantPresencePlanning) return null;
    return `${baseWsPlanning}/api/v1/ws/planning/${salonPlanningId}?user=${encodeURIComponent(identifiantPresencePlanning)}&username=${encodeURIComponent(nomPresencePlanning)}`;
  }, [dateDebut, identifiantPresencePlanning, nomPresencePlanning]);

  const {
    connecte: synchroPlanningActive,
    utilisateurs: participantsPlanning,
    envoyer: diffuserPlanning,
    mode: modeSynchroPlanning,
  } = utiliserWebSocket({
    url: urlWsPlanning,
    gestionnaires: {
      repas_added: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
          invalider(["planning", "nutrition"]);
        }
      },
      repas_updated: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
          invalider(["planning", "nutrition"]);
        }
      },
      repas_removed: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
          invalider(["planning", "nutrition"]);
        }
      },
      slot_swapped: (message) => {
        if (String(message.user_id ?? "") !== identifiantPresencePlanning) {
          invalider(["planning"]);
        }
      },
    },
    maxTentatives: 3,
  });

  return {
    identifiantPresencePlanning,
    synchroPlanningActive,
    participantsPlanning,
    diffuserPlanning,
    modeSynchroPlanning,
  };
}
