"use client";

import { useMemo } from "react";

import { evaluerRappelsFamille } from "@/bibliotheque/api/famille";
import { obtenirAlertes } from "@/bibliotheque/api/inventaire";
import { obtenirAlertesJeux } from "@/bibliotheque/api/jeux";
import { obtenirTachesJourMaison } from "@/bibliotheque/api/maison";
import { utiliserRequete } from "@/crochets/utiliser-api";
import type { RappelFamille } from "@/types/famille";

export function utiliserBadgesModules() {
  const { data: rappelsData } = utiliserRequete<{ rappels: RappelFamille[]; total: number }>(
    ["famille", "rappels", "badge"],
    evaluerRappelsFamille,
    { staleTime: 5 * 60 * 1000, refetchInterval: 10 * 60 * 1000 }
  );

  const { data: alertesCuisine } = utiliserRequete(
    ["cuisine", "inventaire", "alertes", "badge"],
    obtenirAlertes,
    { staleTime: 5 * 60 * 1000, refetchInterval: 10 * 60 * 1000 }
  );

  const { data: tachesMaison } = utiliserRequete(
    ["maison", "taches-jour", "badge"],
    obtenirTachesJourMaison,
    { staleTime: 5 * 60 * 1000, refetchInterval: 10 * 60 * 1000 }
  );

  const { data: alertesJeux } = utiliserRequete(
    ["jeux", "alertes", "badge"],
    () => obtenirAlertesJeux(),
    { staleTime: 5 * 60 * 1000, refetchInterval: 10 * 60 * 1000 }
  );

  const badges = useMemo(
    () => ({
      cuisine: Array.isArray(alertesCuisine) ? alertesCuisine.length : 0,
      famille: rappelsData?.rappels?.filter((r) => r.priorite === "danger").length ?? 0,
      maison: Array.isArray(tachesMaison) ? tachesMaison.filter((t) => !t.fait).length : 0,
      jeux: Array.isArray(alertesJeux) ? alertesJeux.length : 0,
    }),
    [alertesCuisine, alertesJeux, rappelsData?.rappels, tachesMaison]
  );

  return {
    badges,
    badgePlus: badges.jeux,
  };
}
