"""
Dispatcher multi-canal pour les notifications.

Centralise l'envoi de notifications sur tous les canaux disponibles :
- ntfy.sh (push via topic)
- Web Push (VAPID)
- Email (Resend)

Usage :
    dispatcher = get_dispatcher_notifications()
    resultats = dispatcher.envoyer(user_id, "Message", canaux=["email", "ntfy"])
    # → {"email": True, "ntfy": True}
"""

import logging
from typing import Any

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class DispatcherNotifications:
    """Dispatcher multi-canal : email / push / ntfy."""

    def envoyer(
        self,
        user_id: str,
        message: str,
        canaux: list[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, bool]:
        """
        Envoie une notification sur les canaux demandés.

        Args:
            user_id: Identifiant de l'utilisateur destinataire.
            message: Corps du message.
            canaux: Liste de canaux à utiliser. Par défaut ["ntfy", "push"].
            **kwargs: Paramètres supplémentaires par canal :
                - email: str (adresse email si canal "email")
                - titre: str (titre de la notification)
                - sujet: str (sujet email, sinon utilise ``titre``)
                - type_email: str (nom de méthode ServiceEmail, ex. "alerte_critique")
                - alerte: dict (pour envoyer_alerte_critique)
                - priorite: int (priorité ntfy 1–5)
                - tags: list[str] (tags ntfy)

        Returns:
            Dictionnaire ``{canal: succès}`` pour chaque canal demandé.
        """
        if canaux is None:
            canaux = ["ntfy", "push"]

        resultats: dict[str, bool] = {}

        for canal in canaux:
            try:
                if canal == "ntfy":
                    resultats[canal] = self._envoyer_ntfy(message, **kwargs)
                elif canal == "push":
                    resultats[canal] = self._envoyer_push(user_id, message, **kwargs)
                elif canal == "email":
                    resultats[canal] = self._envoyer_email(user_id, message, **kwargs)
                elif canal == "whatsapp":
                    resultats[canal] = self._envoyer_whatsapp(message, **kwargs)
                else:
                    logger.warning("Canal de notification inconnu : %s", canal)
                    resultats[canal] = False
            except Exception as e:
                logger.error("Erreur envoi canal %s : %s", canal, e)
                resultats[canal] = False

        return resultats

    # ─── Canal ntfy ────────────────────────────────────────────────────────────

    def _envoyer_ntfy(self, message: str, **kwargs: Any) -> bool:
        """Envoie via ntfy.sh."""
        try:
            import asyncio

            from src.services.core.notifications.notif_ntfy import obtenir_service_ntfy
            from src.services.core.notifications.types import NotificationNtfy

            service = obtenir_service_ntfy()
            notif = NotificationNtfy(
                titre=kwargs.get("titre", "Matanne"),
                message=message,
                priorite=kwargs.get("priorite", 3),
                tags=kwargs.get("tags", []),
            )

            async def _send():
                return await service.envoyer(notif)

            resultat = asyncio.run(_send())
            return bool(getattr(resultat, "succes", False))
        except Exception as e:
            logger.error("Erreur ntfy : %s", e)
            return False

    # ─── Canal Web Push ─────────────────────────────────────────────────────────

    def _envoyer_push(self, user_id: str, message: str, **kwargs: Any) -> bool:
        """Envoie via Web Push (VAPID)."""
        try:
            from src.services.core.notifications.notif_web_core import get_push_notification_service

            service = get_push_notification_service()
            titre = kwargs.get("titre", "Matanne")

            if hasattr(service, "creer_notification_generique"):
                notif = service.creer_notification_generique(titre, message)
                nb = service.envoyer_a_utilisateur(user_id, notif) if hasattr(
                    service, "envoyer_a_utilisateur"
                ) else service.envoyer_a_tous(notif)
                return nb > 0
            return False
        except Exception as e:
            logger.error("Erreur push web : %s", e)
            return False

    # ─── Canal WhatsApp ─────────────────────────────────────────────────────────

    def _envoyer_whatsapp(self, message: str, **kwargs: Any) -> bool:
        """Envoie via WhatsApp Meta Cloud API."""
        try:
            import asyncio
            from src.services.integrations.whatsapp import (
                envoyer_message_whatsapp,
                envoyer_liste_courses_partagee,
                envoyer_rapport_hebdo_whatsapp,
            )
            from src.core.config import obtenir_parametres

            settings = obtenir_parametres()
            destinataire = getattr(settings, "WHATSAPP_USER_NUMBER", None)
            if not destinataire:
                logger.debug("WhatsApp : WHATSAPP_USER_NUMBER non configuré, canal ignoré")
                return False

            type_wa = kwargs.get("type_whatsapp", "texte")

            async def _send() -> bool:
                if type_wa == "liste_courses":
                    articles = kwargs.get("articles", [message])
                    nom_liste = kwargs.get("nom_liste", "Courses")
                    return await envoyer_liste_courses_partagee(articles, nom_liste)
                elif type_wa == "rapport_hebdo":
                    return await envoyer_rapport_hebdo_whatsapp(message)
                else:
                    return await envoyer_message_whatsapp(destinataire, message)

            return asyncio.run(_send())
        except Exception as e:
            logger.error("Erreur WhatsApp : %s", e)
            return False

    # ─── Canal email ────────────────────────────────────────────────────────────

    def _envoyer_email(self, user_id: str, message: str, **kwargs: Any) -> bool:
        email = kwargs.get("email")
        if not email:
            # Essayer de récupérer l'email depuis la DB
            email = self._recuperer_email_utilisateur(user_id)
        if not email:
            logger.warning("Email inconnu pour user_id=%s, canal email ignoré", user_id)
            return False

        from src.services.core.notifications.notif_email import get_service_email

        service_email = get_service_email()
        type_email = kwargs.get("type_email", "alerte_critique")

        if type_email == "alerte_critique":
            alerte = kwargs.get("alerte", {
                "titre": kwargs.get("titre", "Notification Matanne"),
                "message": message,
            })
            return service_email.envoyer_alerte_critique(email, alerte)
        elif type_email == "resume_hebdo":
            return service_email.envoyer_resume_hebdo(email, kwargs.get("resume", {"semaine": "", "resume_ia": message}))
        elif type_email == "rapport_mensuel":
            return service_email.envoyer_rapport_mensuel(email, kwargs.get("rapport", {}))
        elif type_email == "invitation":
            return service_email.envoyer_invitation_famille(email, kwargs.get("invitant", "Matanne"))
        else:
            # Générique : alerte critique avec le message
            return service_email.envoyer_alerte_critique(email, {
                "titre": kwargs.get("titre", "Notification"),
                "message": message,
            })

    # ─── Helpers ────────────────────────────────────────────────────────────────

    def _recuperer_email_utilisateur(self, user_id: str) -> str | None:
        """Récupère l'email d'un utilisateur depuis la DB."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.users import ProfilUtilisateur

            with obtenir_contexte_db() as session:
                profil = (
                    session.query(ProfilUtilisateur)
                    .filter(ProfilUtilisateur.username == user_id)
                    .first()
                )
                if profil:
                    return getattr(profil, "email", None)
        except Exception as e:
            logger.debug("Impossible de récupérer email pour user_id=%s : %s", user_id, e)
        return None


# ─── Factory ───────────────────────────────────────────────────────────────────


@service_factory("dispatcher_notifications", tags={"notifications"})
def get_dispatcher_notifications() -> DispatcherNotifications:
    """Retourne le singleton DispatcherNotifications."""
    return DispatcherNotifications()
