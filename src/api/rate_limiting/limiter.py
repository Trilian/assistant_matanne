"""
Limiteur de débit principal.
"""

import logging
from typing import Any

from fastapi import HTTPException, Request, Response

from .config import ConfigLimitationDebit, config_limitation_debit
from .storage import StockageLimitationDebit, _stockage

logger = logging.getLogger(__name__)


class LimiteurDebit:
    """Limiteur de débit principal. Supporte plusieurs fenêtres de temps."""

    def __init__(
        self,
        stockage: StockageLimitationDebit | None = None,
        config: ConfigLimitationDebit | None = None,
    ):
        self.stockage = stockage or _stockage
        self.config = config or config_limitation_debit

    def _generer_cle(
        self,
        request: Request,
        identifiant: str | None = None,
        endpoint: str | None = None,
    ) -> str:
        """Génère une clé unique pour la limitation de débit."""
        parties = []
        if identifiant:
            parties.append(f"user:{identifiant}")
        else:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            else:
                ip = request.client.host if request.client else "unknown"
            parties.append(f"ip:{ip}")
        if endpoint:
            parties.append(f"endpoint:{endpoint}")
        return ":".join(parties)

    def verifier_limite(
        self,
        request: Request,
        id_utilisateur: str | None = None,
        est_premium: bool = False,
        est_endpoint_ia: bool = False,
    ) -> dict[str, Any]:
        """
        Vérifie la limite de débit et retourne les informations.

        Args:
            request: Requête FastAPI
            id_utilisateur: ID utilisateur (si authentifié)
            est_premium: Utilisateur premium
            est_endpoint_ia: Endpoint utilisant l'IA

        Returns:
            Dict avec: allowed, limit, remaining, reset, retry_after

        Raises:
            HTTPException: Si limite dépassée
        """
        if request.url.path in self.config.chemins_exemptes:
            return {"allowed": True, "limit": -1, "remaining": -1}

        cle = self._generer_cle(request, id_utilisateur)

        if self.stockage.est_bloque(cle):
            raise HTTPException(
                status_code=429,
                detail="Trop de requêtes. Réessayez plus tard.",
                headers={"Retry-After": "60"},
            )

        # Déterminer les limites
        if est_endpoint_ia:
            limite_minute = self.config.requetes_ia_par_minute
            limite_heure = self.config.requetes_ia_par_heure
            limite_jour = self.config.requetes_ia_par_jour
        elif est_premium:
            limite_minute = self.config.requetes_premium_par_minute
            limite_heure = self.config.requetes_par_heure * 2
            limite_jour = self.config.requetes_par_jour * 2
        elif id_utilisateur:
            limite_minute = self.config.requetes_authentifie_par_minute
            limite_heure = self.config.requetes_par_heure
            limite_jour = self.config.requetes_par_jour
        else:
            limite_minute = self.config.requetes_anonyme_par_minute
            limite_heure = self.config.requetes_par_heure // 2
            limite_jour = self.config.requetes_par_jour // 2

        fenetres = [
            ("minute", 60, limite_minute),
            ("hour", 3600, limite_heure),
            ("day", 86400, limite_jour),
        ]

        plus_restrictif = None

        for nom_fenetre, fenetre_secondes, limite in fenetres:
            cle_fenetre = f"{cle}:{nom_fenetre}"
            compte = self.stockage.incrementer(cle_fenetre, fenetre_secondes)

            if compte > limite:
                reset = self.stockage.obtenir_temps_reset(cle_fenetre, fenetre_secondes)

                if compte > limite * 2:
                    self.stockage.bloquer(cle, 300)
                    logger.warning(f"Abus détecté: {cle}")

                raise HTTPException(
                    status_code=429,
                    detail=f"Limite de requêtes dépassée ({nom_fenetre}). Réessayez dans {reset}s.",
                    headers={
                        "X-RateLimit-Limit": str(limite),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset),
                        "Retry-After": str(reset),
                    },
                )

            restant = limite - compte
            reset = self.stockage.obtenir_temps_reset(cle_fenetre, fenetre_secondes)

            if plus_restrictif is None or restant < plus_restrictif["remaining"]:
                plus_restrictif = {
                    "allowed": True,
                    "limit": limite,
                    "remaining": restant,
                    "reset": reset,
                    "window": nom_fenetre,
                }

        return plus_restrictif or {"allowed": True}

    def ajouter_headers(self, response: Response, info_limite: dict[str, Any]):
        """Ajoute les headers de limitation de débit à la réponse."""
        if not self.config.activer_headers:
            return
        if info_limite.get("limit", -1) >= 0:
            response.headers["X-RateLimit-Limit"] = str(info_limite.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(info_limite.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(info_limite.get("reset", 0))


# Instance globale
limiteur_debit = LimiteurDebit()
