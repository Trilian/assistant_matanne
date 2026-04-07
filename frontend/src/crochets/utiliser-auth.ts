// ═══════════════════════════════════════════════════════════
// Hook useAuth — Authentification
// ═══════════════════════════════════════════════════════════

"use client";

import { useCallback, useEffect } from "react";
import { utiliserStoreAuth } from "@/magasins/store-auth";
import { obtenirProfil, deconnecter as apiDeconnecter } from "@/bibliotheque/api/auth";

/**
 * Hook d'authentification — charge le profil JWT au montage et expose les actions de session.
 * @returns {{ utilisateur, estConnecte, estChargement, deconnecter }}
 */
export function utiliserAuth() {
  const { utilisateur, estConnecte, estChargement, definirUtilisateur, definirChargement, reinitialiser } =
    utiliserStoreAuth();

  // Charger le profil au montage si un token existe
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token && !utilisateur) {
      definirChargement(true);
      obtenirProfil()
        .then(definirUtilisateur)
        .catch(() => {
          localStorage.removeItem("access_token");
          definirUtilisateur(null);
        })
        .finally(() => definirChargement(false));
    } else {
      // Pas de token — auth terminée immédiatement
      definirChargement(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const deconnecter = useCallback(() => {
    reinitialiser();
    apiDeconnecter();
  }, [reinitialiser]);

  return { utilisateur, user: utilisateur, estConnecte, estChargement, deconnecter };
}
