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
from collections import defaultdict
from datetime import datetime
from typing import Any

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

_CANAUX_VALIDES = {"ntfy", "push", "email", "whatsapp"}

# Mapping Phase 8 (§11.4): événement -> catégorie + canaux cibles
_MAPPING_EVENEMENTS_CANAUX: dict[str, dict[str, Any]] = {
    "peremption_j2": {"categorie": "alertes", "canaux": ["push", "ntfy"]},
    "rappel_courses": {"categorie": "rappels", "canaux": ["push", "ntfy", "whatsapp"]},
    "resume_hebdo": {"categorie": "resumes", "canaux": ["whatsapp", "email"]},
    "rapport_budget_mensuel": {"categorie": "resumes", "canaux": ["email"]},
    "anniversaire_j7": {"categorie": "rappels", "canaux": ["push", "ntfy", "whatsapp"]},
    "tache_entretien_urgente": {
        "categorie": "alertes",
        "canaux": ["push", "ntfy", "whatsapp"],
    },
    "echec_cron_job": {
        "categorie": "alertes",
        "canaux": ["push", "ntfy", "whatsapp", "email"],
    },
    "document_expirant": {"categorie": "alertes", "canaux": ["push", "ntfy", "email"]},
    "recolte_jardin_prete": {"categorie": "rappels", "canaux": ["push", "ntfy"]},
    "badge_debloque": {"categorie": "rappels", "canaux": ["push", "ntfy"]},
    "diagnostic_maison_alerte": {"categorie": "alertes", "canaux": ["whatsapp", "push", "email"]},
    "budget_depassement": {"categorie": "alertes", "canaux": ["whatsapp", "push", "ntfy"]},
}


class DispatcherNotifications:
    """Dispatcher multi-canal : email / push / ntfy."""

    _FALLBACK_CANAUX: dict[str, list[str]] = {
        "push": ["ntfy", "whatsapp", "email"],
        "ntfy": ["push", "whatsapp", "email"],
        "whatsapp": ["push", "email"],
        "email": ["push", "ntfy"],
    }

    def __init__(self) -> None:
        # Compteurs in-memory pour le throttling horaire par utilisateur.
        self._compteurs_heure: dict[str, dict[str, int]] = defaultdict(dict)
        # File de digest in-memory (consolidation des notifications non urgentes).
        self._digest_queue: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def envoyer(
        self,
        user_id: str,
        message: str,
        canaux: list[str] | None = None,
        type_evenement: str | None = None,
        categorie: str | None = None,
        forcer: bool = False,
        **kwargs: Any,
    ) -> dict[str, bool]:
        """
        Envoie une notification sur les canaux demandés.

        Args:
            user_id: Identifiant de l'utilisateur destinataire.
            message: Corps du message.
            canaux: Liste de canaux à utiliser. Si absent, dérivé de l'événement/prefs.
            type_evenement: Type d'événement métier (mapping Phase 8).
            categorie: Catégorie métier (rappels|alertes|resumes).
            forcer: Si True, ignore les règles de throttling/digest.
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
        canaux = self._resoudre_canaux(
            user_id=user_id,
            canaux=canaux,
            type_evenement=type_evenement,
            categorie=categorie,
        )

        if not canaux:
            return {}

        strategie = str(kwargs.get("strategie", "parallel")).lower()
        sequence = canaux
        if strategie == "failover":
            sequence = self._construire_sequence_failover(canaux)

        if not forcer and not self._peut_envoyer(user_id=user_id):
            self._enregistrer_digest(user_id, message, type_evenement, categorie, sequence)
            return {"digest": True}

        if not forcer and self._mode_digest_actif(user_id=user_id, categorie=categorie):
            self._enregistrer_digest(user_id, message, type_evenement, categorie, sequence)
            return {"digest": True}

        resultats: dict[str, bool] = {}

        for canal in sequence:
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

            if strategie == "failover" and resultats.get(canal):
                if len(resultats) > 1:
                    canaux_echoues = [c for c, ok in resultats.items() if not ok]
                    logger.info(
                        "Failover réussi via '%s' après échec(s) : %s",
                        canal,
                        ", ".join(canaux_echoues) or "aucun",
                    )
                break
            elif strategie == "failover" and not resultats.get(canal):
                logger.warning(
                    "Failover canal '%s' échoué, tentative canal suivant…", canal
                )

        if any(resultats.values()):
            self._incrementer_compteur(user_id)

        return resultats

    def envoyer_evenement(
        self,
        user_id: str,
        type_evenement: str,
        message: str,
        **kwargs: Any,
    ) -> dict[str, bool]:
        """Envoi orienté événement métier avec routing auto + failover."""
        mapping = _MAPPING_EVENEMENTS_CANAUX.get(type_evenement, {})
        categorie = mapping.get("categorie")
        kwargs.setdefault("strategie", "failover")
        return self.envoyer(
            user_id=user_id,
            message=message,
            type_evenement=type_evenement,
            categorie=categorie,
            **kwargs,
        )

    def vider_digest(self, user_id: str) -> dict[str, bool]:
        """Envoie un digest compact puis vide la file d'attente utilisateur."""
        items = self._digest_queue.get(user_id, [])
        if not items:
            return {"digest": False}

        lignes = [i.get("message", "") for i in items[-10:] if i.get("message")]
        resultats = self.envoyer(
            user_id=user_id,
            message="\n".join(f"- {ligne}" for ligne in lignes),
            canaux=["email", "whatsapp", "ntfy"],
            categorie="resumes",
            strategie="failover",
            forcer=True,
            titre="Résumé notifications",
        )
        if any(resultats.values()):
            self._digest_queue[user_id] = []
        return resultats

    def lister_users_digest_pending(self) -> list[str]:
        """Retourne les user_id ayant au moins un message en attente de digest."""
        return sorted([uid for uid, items in self._digest_queue.items() if items])

    def _construire_sequence_failover(self, canaux: list[str]) -> list[str]:
        """Construit une chaîne de canaux ordonnée avec fallback sans doublons."""
        sequence: list[str] = []
        for canal in canaux:
            sequence.append(canal)
            sequence.extend(self._FALLBACK_CANAUX.get(canal, []))

        vue: set[str] = set()
        resultat: list[str] = []
        for canal in sequence:
            if canal not in vue:
                vue.add(canal)
                resultat.append(canal)
        return resultat

    def _resoudre_canaux(
        self,
        user_id: str,
        canaux: list[str] | None,
        type_evenement: str | None,
        categorie: str | None,
    ) -> list[str]:
        if canaux:
            return [c for c in canaux if c in _CANAUX_VALIDES]

        mapping = _MAPPING_EVENEMENTS_CANAUX.get(type_evenement or "", {})
        categorie_cible = categorie or mapping.get("categorie")
        canaux_mapping = [c for c in mapping.get("canaux", []) if c in _CANAUX_VALIDES]

        prefs = self._recuperer_preferences_notifications(user_id)
        canaux_par_categorie = prefs.get("canaux_par_categorie", {}) or {}

        if categorie_cible and categorie_cible in canaux_par_categorie:
            canaux_prefs = [c for c in (canaux_par_categorie.get(categorie_cible) or []) if c in _CANAUX_VALIDES]
            if canaux_mapping:
                intersection = [c for c in canaux_mapping if c in canaux_prefs]
                extras = [c for c in canaux_prefs if c not in intersection]
                if intersection or extras:
                    return intersection + extras
            if canaux_prefs:
                return canaux_prefs

        if canaux_mapping:
            return canaux_mapping

        canal_prefere = prefs.get("canal_prefere", "push")
        if canal_prefere in _CANAUX_VALIDES:
            return [canal_prefere]
        return ["ntfy", "push"]

    def _recuperer_preferences_notifications(self, user_id: str) -> dict[str, Any]:
        """Charge les préférences notifications de l'utilisateur (best-effort)."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.notifications import PreferenceNotification

            with obtenir_contexte_db() as session:
                prefs = (
                    session.query(PreferenceNotification)
                    .filter(PreferenceNotification.user_id == user_id)
                    .first()
                )
                if not prefs:
                    return {}

                return {
                    "canal_prefere": getattr(prefs, "canal_prefere", "push"),
                    "canaux_par_categorie": getattr(prefs, "canaux_par_categorie", {}) or {},
                    "modules_actifs": getattr(prefs, "modules_actifs", {}) or {},
                }
        except Exception as exc:
            logger.debug("Préférences notifications indisponibles pour %s: %s", user_id, exc)
        return {}

    def _cle_heure(self) -> str:
        return datetime.now().strftime("%Y%m%d%H")

    def _incrementer_compteur(self, user_id: str) -> None:
        key = self._cle_heure()
        compteurs = self._compteurs_heure[user_id]
        compteurs[key] = compteurs.get(key, 0) + 1

    def _peut_envoyer(self, user_id: str) -> bool:
        key = self._cle_heure()
        prefs = self._recuperer_preferences_notifications(user_id)
        modules_actifs = prefs.get("modules_actifs", {}) or {}
        max_par_heure = int(modules_actifs.get("max_par_heure", 5))
        current = self._compteurs_heure[user_id].get(key, 0)
        return current < max_par_heure

    def _mode_digest_actif(self, user_id: str, categorie: str | None) -> bool:
        # Les alertes critiques restent envoyées immédiatement.
        if categorie == "alertes":
            return False
        prefs = self._recuperer_preferences_notifications(user_id)
        modules_actifs = prefs.get("modules_actifs", {}) or {}
        return bool(modules_actifs.get("mode_digest", False))

    def _enregistrer_digest(
        self,
        user_id: str,
        message: str,
        type_evenement: str | None,
        categorie: str | None,
        canaux: list[str],
    ) -> None:
        self._digest_queue[user_id].append(
            {
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "type_evenement": type_evenement,
                "categorie": categorie,
                "canaux": canaux,
            }
        )

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
                envoyer_suggestion_recette_du_jour,
                envoyer_alerte_diagnostic_maison,
                envoyer_resume_weekend_suggestions,
                envoyer_alerte_budget_depassement,
                envoyer_bilan_nutrition_semaine,
                envoyer_rappel_entretien_maison,
            )
            from src.core.config import obtenir_parametres

            settings = obtenir_parametres()
            destinataire = getattr(settings, "WHATSAPP_USER_NUMBER", None)
            if not destinataire:
                logger.debug("WhatsApp : WHATSAPP_USER_NUMBER non configuré, canal ignoré")
                return False

            type_wa = kwargs.get("type_whatsapp", "texte")

            async def _send() -> bool:
                if type_wa in {"liste_courses", "articles_courses"}:
                    articles = kwargs.get("articles", [message])
                    nom_liste = kwargs.get("nom_liste", "Courses")
                    return await envoyer_liste_courses_partagee(articles, nom_liste)
                elif type_wa == "rapport_hebdo":
                    return await envoyer_rapport_hebdo_whatsapp(message)
                elif type_wa == "recette_du_jour":
                    return await envoyer_suggestion_recette_du_jour(message)
                elif type_wa == "diagnostic_maison":
                    return await envoyer_alerte_diagnostic_maison(message)
                elif type_wa == "resume_weekend":
                    return await envoyer_resume_weekend_suggestions(message)
                elif type_wa == "budget_depassement":
                    return await envoyer_alerte_budget_depassement(message)
                elif type_wa == "bilan_nutrition":
                    return await envoyer_bilan_nutrition_semaine(message)
                elif type_wa == "rappel_entretien":
                    return await envoyer_rappel_entretien_maison(message)
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
        elif type_email == "rapport_famille_mensuel_complet":
            return service_email.envoyer_rapport_famille_mensuel_complet(email, kwargs.get("rapport", {}))
        elif type_email == "rapport_maison_trimestriel":
            return service_email.envoyer_rapport_maison_trimestriel(email, kwargs.get("rapport", {}))
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
