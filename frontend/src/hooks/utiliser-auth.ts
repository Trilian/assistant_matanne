// ═══════════════════════════════════════════════════════════
// Hook useAuth — Authentification
// ═══════════════════════════════════════════════════════════

"use client";

import { useCallback, useEffect } from "react";
import { utiliserStoreAuth } from "@/stores/store-auth";
import { obtenirProfil, deconnecter as apiDeconnecter } from "@/lib/api/auth";

export function utiliserAuth() {
  const { utilisateur, estConnecte, estChargement, definirUtilisateur, reinitialiser } =
    utiliserStoreAuth();

  // Charger le profil au montage si un token existe
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token && !utilisateur) {
      obtenirProfil()
        .then(definirUtilisateur)
        .catch(() => {
          localStorage.removeItem("access_token");
          definirUtilisateur(null);
        });
    } else if (!token) {
      definirUtilisateur(null);
    }
  }, [utilisateur, definirUtilisateur]);

  const deconnecter = useCallback(() => {
    reinitialiser();
    apiDeconnecter();
  }, [reinitialiser]);

  return { utilisateur, estConnecte, estChargement, deconnecter };
}
