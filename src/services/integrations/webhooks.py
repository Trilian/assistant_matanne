"""
Service de webhooks sortants.

Gère le CRUD des abonnements webhook et la livraison des événements
vers des URLs externes avec signature HMAC-SHA256, retry et auto-désactivation.

Usage:
    from src.services.webhooks import get_webhook_service

    service = get_webhook_service()
    service.creer_webhook(url="https://...", evenements=["recette.*"], user_id="xxx")
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

import httpx

from src.services.core.event_bus_mixin import emettre_evenement_simple
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Thread pool pour les livraisons fire-and-forget
_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="webhook")

# Seuil d'échecs consécutifs avant auto-désactivation
MAX_ECHECS_CONSECUTIFS = 5


class WebhookService:
    """Service de gestion des webhooks sortants.

    Responsabilités:
    - CRUD des abonnements webhook
    - Livraison des événements avec signature HMAC-SHA256
    - Retry avec backoff exponentiel (3 tentatives)
    - Auto-désactivation après MAX_ECHECS_CONSECUTIFS échecs
    - Test de connectivité d'un webhook
    """

    def creer_webhook(
        self,
        url: str,
        evenements: list[str],
        user_id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Crée un nouvel abonnement webhook avec un secret généré.

        Args:
            url: URL de destination (recevra les POST)
            evenements: Patterns d'événements (ex: ["recette.*", "courses.generees"])
            user_id: ID du propriétaire
            description: Description libre

        Returns:
            Dict avec les données du webhook créé incluant le secret
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        secret = secrets.token_hex(32)

        with obtenir_contexte_db() as session:
            webhook = WebhookAbonnement(
                url=str(url),
                evenements=evenements,
                secret=secret,
                actif=True,
                description=description,
                user_id=user_id,
                nb_echecs_consecutifs=0,
            )
            session.add(webhook)
            session.commit()
            session.refresh(webhook)

            logger.info(f"🔗 Webhook #{webhook.id} créé → {url} ({evenements})")

            emettre_evenement_simple(
                "webhook.modifie",
                {"webhook_id": webhook.id, "url": str(url), "action": "cree"},
                source="webhooks",
            )

            return {
                "id": webhook.id,
                "url": webhook.url,
                "evenements": webhook.evenements,
                "secret": secret,
                "actif": webhook.actif,
                "description": webhook.description,
                "derniere_livraison": webhook.derniere_livraison,
                "nb_echecs_consecutifs": webhook.nb_echecs_consecutifs,
                "cree_le": getattr(webhook, "cree_le", None),
                "modifie_le": getattr(webhook, "modifie_le", None),
            }

    def lister_webhooks(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """Liste les webhooks, optionnellement filtrés par user_id."""
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        with obtenir_contexte_db() as session:
            query = session.query(WebhookAbonnement)
            if user_id:
                query = query.filter(WebhookAbonnement.user_id == user_id)
            webhooks = query.order_by(WebhookAbonnement.id.desc()).all()

            return [self._to_dict(wh) for wh in webhooks]

    def obtenir_webhook(self, webhook_id: int) -> dict[str, Any] | None:
        """Récupère un webhook par son ID."""
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        with obtenir_contexte_db() as session:
            webhook = (
                session.query(WebhookAbonnement).filter(WebhookAbonnement.id == webhook_id).first()
            )
            return self._to_dict(webhook) if webhook else None

    def modifier_webhook(self, webhook_id: int, **kwargs: Any) -> dict[str, Any] | None:
        """Modifie un webhook existant.

        Args:
            webhook_id: ID du webhook
            **kwargs: Champs à modifier (url, evenements, actif, description)

        Returns:
            Le webhook modifié ou None si non trouvé
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        with obtenir_contexte_db() as session:
            webhook = (
                session.query(WebhookAbonnement).filter(WebhookAbonnement.id == webhook_id).first()
            )

            if not webhook:
                return None

            for key, value in kwargs.items():
                if value is not None and hasattr(webhook, key):
                    if key == "url":
                        value = str(value)
                    setattr(webhook, key, value)

            # Réinitialiser le compteur d'échecs si réactivé
            if kwargs.get("actif") is True:
                webhook.nb_echecs_consecutifs = 0

            session.commit()
            session.refresh(webhook)

            logger.info(f"🔗 Webhook #{webhook_id} modifié")

            emettre_evenement_simple(
                "webhook.modifie",
                {"webhook_id": webhook_id, "action": "modifie"},
                source="webhooks",
            )
            return self._to_dict(webhook)

    def supprimer_webhook(self, webhook_id: int) -> bool:
        """Supprime un webhook. Retourne True si trouvé et supprimé."""
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        with obtenir_contexte_db() as session:
            webhook = (
                session.query(WebhookAbonnement).filter(WebhookAbonnement.id == webhook_id).first()
            )
            if not webhook:
                return False

            session.delete(webhook)
            session.commit()

            logger.info(f"🔗 Webhook #{webhook_id} supprimé")

            emettre_evenement_simple(
                "webhook.modifie",
                {"webhook_id": webhook_id, "action": "supprime"},
                source="webhooks",
            )
            return True

    def tester_webhook(self, webhook_id: int) -> dict[str, Any]:
        """Envoie un ping de test à un webhook.

        Returns:
            Dict avec success, status_code, response_time_ms, error
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        with obtenir_contexte_db() as session:
            webhook = (
                session.query(WebhookAbonnement).filter(WebhookAbonnement.id == webhook_id).first()
            )

            if not webhook:
                return {
                    "success": False,
                    "status_code": None,
                    "response_time_ms": None,
                    "error": "Webhook non trouvé",
                }

            payload = {
                "type": "webhook.test",
                "data": {"message": "Ceci est un test de connectivité webhook"},
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return self._livrer_payload(webhook.url, webhook.secret, payload)

    def livrer_evenement(self, type_evenement: str, data: dict[str, Any]) -> int:
        """Livre un événement à tous les webhooks actifs qui matchent le pattern.

        Exécution fire-and-forget via thread pool pour ne pas bloquer le bus.

        Args:
            type_evenement: Type de l'événement (ex: "recette.planifiee")
            data: Données de l'événement

        Returns:
            Nombre de webhooks qui seront notifiés
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.notifications import WebhookAbonnement

        with obtenir_contexte_db() as session:
            webhooks_actifs = (
                session.query(WebhookAbonnement).filter(WebhookAbonnement.actif.is_(True)).all()
            )

            # Collecter les webhooks qui matchent le pattern
            webhooks_a_notifier = []
            for wh in webhooks_actifs:
                if self._match_patterns(type_evenement, wh.evenements):
                    webhooks_a_notifier.append(
                        {
                            "id": wh.id,
                            "url": wh.url,
                            "secret": wh.secret,
                        }
                    )

        # Livrer en fire-and-forget
        payload = {
            "type": type_evenement,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        for wh_info in webhooks_a_notifier:
            _executor.submit(
                self._livrer_avec_retry,
                wh_info["id"],
                wh_info["url"],
                wh_info["secret"],
                payload,
            )

        if webhooks_a_notifier:
            logger.debug(f"🔗 Événement '{type_evenement}' → {len(webhooks_a_notifier)} webhook(s)")

        return len(webhooks_a_notifier)

    # ───────────────────────────────────────────────────
    # Méthodes privées
    # ───────────────────────────────────────────────────

    @staticmethod
    def _match_patterns(type_evenement: str, patterns: list[str]) -> bool:
        """Vérifie si un type d'événement matche au moins un pattern.

        Supporte:
        - Match exact: "recette.planifiee" == "recette.planifiee"
        - Wildcard: "recette.*" match "recette.planifiee", "recette.importee"
        - Global: "*" match tout
        """
        for pattern in patterns:
            if pattern == "*":
                return True
            if pattern == type_evenement:
                return True
            if pattern.endswith(".*"):
                prefix = pattern[:-2]
                if type_evenement.startswith(prefix + "."):
                    return True
        return False

    @staticmethod
    def _signer_payload(secret: str, payload_bytes: bytes) -> str:
        """Génère la signature HMAC-SHA256 du payload."""
        return hmac.new(
            secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

    def _livrer_payload(self, url: str, secret: str, payload: dict) -> dict[str, Any]:
        """Envoie un payload à une URL avec signature HMAC.

        Returns:
            Dict avec success, status_code, response_time_ms, error
        """
        payload_bytes = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        signature = self._signer_payload(secret, payload_bytes)

        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Event": payload.get("type", "unknown"),
            "X-Webhook-Timestamp": payload.get("timestamp", ""),
            "User-Agent": "AssistantMatanne-Webhook/1.0",
        }

        start = time.monotonic()
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, content=payload_bytes, headers=headers)

            elapsed_ms = (time.monotonic() - start) * 1000
            success = 200 <= response.status_code < 300

            return {
                "success": success,
                "status_code": response.status_code,
                "response_time_ms": round(elapsed_ms, 1),
                "error": None if success else f"HTTP {response.status_code}",
            }
        except httpx.TimeoutException:
            elapsed_ms = (time.monotonic() - start) * 1000
            return {
                "success": False,
                "status_code": None,
                "response_time_ms": round(elapsed_ms, 1),
                "error": "Timeout (10s)",
            }
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            return {
                "success": False,
                "status_code": None,
                "response_time_ms": round(elapsed_ms, 1),
                "error": str(e),
            }

    def _livrer_avec_retry(
        self,
        webhook_id: int,
        url: str,
        secret: str,
        payload: dict,
        max_retries: int = 3,
    ) -> None:
        """Livre un payload avec retry et backoff exponentiel.

        En cas de MAX_ECHECS_CONSECUTIFS échecs, désactive le webhook.
        """
        backoff_delays = [1, 2, 4]  # secondes

        for attempt in range(max_retries):
            result = self._livrer_payload(url, secret, payload)

            if result["success"]:
                self._marquer_succes(webhook_id)
                return

            if attempt < max_retries - 1:
                time.sleep(backoff_delays[attempt])

        # Tous les retries ont échoué
        self._marquer_echec(webhook_id)
        logger.warning(f"🔗 Webhook #{webhook_id} → échec après {max_retries} tentatives ({url})")

    def _marquer_succes(self, webhook_id: int) -> None:
        """Met à jour le webhook après une livraison réussie."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.notifications import WebhookAbonnement

            with obtenir_contexte_db() as session:
                webhook = (
                    session.query(WebhookAbonnement)
                    .filter(WebhookAbonnement.id == webhook_id)
                    .first()
                )
                if webhook:
                    webhook.derniere_livraison = datetime.now(UTC)
                    webhook.nb_echecs_consecutifs = 0
                    session.commit()
        except Exception as e:
            logger.error(f"Erreur mise à jour webhook #{webhook_id}: {e}")

    def _marquer_echec(self, webhook_id: int) -> None:
        """Incrémente le compteur d'échecs, désactive si seuil atteint."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.notifications import WebhookAbonnement

            with obtenir_contexte_db() as session:
                webhook = (
                    session.query(WebhookAbonnement)
                    .filter(WebhookAbonnement.id == webhook_id)
                    .first()
                )
                if webhook:
                    webhook.nb_echecs_consecutifs += 1
                    if webhook.nb_echecs_consecutifs >= MAX_ECHECS_CONSECUTIFS:
                        webhook.actif = False
                        logger.warning(
                            f"🔗 Webhook #{webhook_id} auto-désactivé "
                            f"({MAX_ECHECS_CONSECUTIFS} échecs consécutifs)"
                        )
                    session.commit()
        except Exception as e:
            logger.error(f"Erreur mise à jour webhook #{webhook_id}: {e}")

    @staticmethod
    def _to_dict(webhook: Any) -> dict[str, Any]:
        """Convertit un modèle WebhookAbonnement en dict."""
        return {
            "id": webhook.id,
            "url": webhook.url,
            "evenements": webhook.evenements,
            "secret": webhook.secret,
            "actif": webhook.actif,
            "description": webhook.description,
            "derniere_livraison": webhook.derniere_livraison,
            "nb_echecs_consecutifs": webhook.nb_echecs_consecutifs,
            "cree_le": getattr(webhook, "cree_le", None),
            "modifie_le": getattr(webhook, "modifie_le", None),
        }


@service_factory("webhooks", tags={"notifications"})
def obtenir_webhook_service() -> WebhookService:
    """Factory singleton pour le service webhooks."""
    return WebhookService()


# ─── Aliases rétrocompatibilité (Sprint 12 A3) ───────────────────────────────
get_webhook_service = obtenir_webhook_service  # alias rétrocompatibilité Sprint 12 A3
