"""
Service inter-modules : Documents expiration → Notifications multi-canal.

IM-P2-3: Alertes automatiques quand des documents famille expirent
(passeport, carte identité, assurance, etc.) à J-30, J-15, J-7.
"""

import logging
from datetime import date, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Seuils d'alerte en jours
SEUILS_ALERTE_JOURS = [30, 15, 7, 1]


class DocumentsNotificationsInteractionService:
    """Service inter-modules Documents → Notifications multi-canal."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def verifier_et_notifier_documents_expirants(
        self,
        user_id: str = "matanne",
        *,
        db=None,
    ) -> dict[str, Any]:
        """Vérifie les documents expirants et envoie les notifications appropriées.

        Envoie des alertes à J-30, J-15, J-7 et J-1 avant expiration.

        Args:
            user_id: ID de l'utilisateur
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec documents vérifiés, alertes envoyées, détails
        """
        from src.core.models import DocumentFamille

        aujourd_hui = date.today()
        alertes_envoyees = []
        documents_verifies = 0

        # Documents avec date d'expiration
        documents = (
            db.query(DocumentFamille)
            .filter(DocumentFamille.date_expiration.isnot(None))
            .all()
        )

        documents_verifies = len(documents)

        for doc in documents:
            if not doc.date_expiration:
                continue

            jours_restants = (doc.date_expiration - aujourd_hui).days

            # Vérifier si on est sur un seuil d'alerte
            for seuil in SEUILS_ALERTE_JOURS:
                if jours_restants == seuil:
                    alerte = self._envoyer_alerte_document(
                        user_id, doc, jours_restants
                    )
                    if alerte:
                        alertes_envoyees.append(alerte)
                    break

            # Document déjà expiré
            if jours_restants < 0 and jours_restants >= -1:
                alerte = self._envoyer_alerte_document(
                    user_id, doc, jours_restants, expire=True
                )
                if alerte:
                    alertes_envoyees.append(alerte)

        message = (
            f"{documents_verifies} document(s) vérifiés, "
            f"{len(alertes_envoyees)} alerte(s) envoyée(s)."
        )
        logger.info(f"✅ Documents→Notifications: {message}")

        return {
            "documents_verifies": documents_verifies,
            "alertes_envoyees": alertes_envoyees,
            "message": message,
        }

    def _envoyer_alerte_document(
        self,
        user_id: str,
        doc: Any,
        jours_restants: int,
        expire: bool = False,
    ) -> dict[str, Any] | None:
        """Envoie une alerte pour un document expirant.

        Args:
            user_id: ID utilisateur
            doc: DocumentFamille instance
            jours_restants: Nombre de jours avant expiration
            expire: True si le document est déjà expiré

        Returns:
            Dict avec détails de l'alerte envoyée, ou None si échec
        """
        if expire:
            titre = f"⚠️ Document expiré : {doc.nom}"
            message = (
                f"Le document '{doc.nom}' ({doc.type_document}) "
                f"a expiré le {doc.date_expiration.isoformat()}. "
                f"Pensez à le renouveler rapidement."
            )
            priorite = 4
        else:
            titre = f"📋 Document expire dans {jours_restants} jour(s) : {doc.nom}"
            message = (
                f"Le document '{doc.nom}' ({doc.type_document}) "
                f"expire le {doc.date_expiration.isoformat()} "
                f"(dans {jours_restants} jour(s)). "
                f"Pensez à prévoir son renouvellement."
            )
            priorite = 3 if jours_restants > 7 else 4

        try:
            from src.services.core.notifications.notif_dispatcher import (
                get_dispatcher_notifications,
            )

            dispatcher = get_dispatcher_notifications()
            resultats = dispatcher.envoyer(
                user_id=user_id,
                message=message,
                type_evenement="document_expirant",
                titre=titre,
                priorite=priorite,
            )

            alerte_info = {
                "document_id": doc.id,
                "nom": doc.nom,
                "type_document": doc.type_document,
                "jours_restants": jours_restants,
                "expire": expire,
                "canaux_resultats": resultats,
            }

            logger.info(
                f"📋 Alerte document envoyée: {doc.nom} "
                f"(J{'+' if expire else '-'}{abs(jours_restants)})"
            )
            return alerte_info

        except Exception as e:
            logger.error(f"Erreur envoi alerte document {doc.nom}: {e}")
            return None

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_resume_expirations(self, *, db=None) -> list[dict[str, Any]]:
        """Retourne un résumé des documents expirants pour le briefing.

        Returns:
            Liste de dicts avec nom, type, date_expiration, jours_restants, urgence
        """
        from src.core.models import DocumentFamille

        aujourd_hui = date.today()
        limite = aujourd_hui + timedelta(days=90)

        documents = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= limite,
            )
            .order_by(DocumentFamille.date_expiration.asc())
            .all()
        )

        result = []
        for doc in documents:
            if not doc.date_expiration:
                continue
            jours = (doc.date_expiration - aujourd_hui).days
            urgence = "expire" if jours < 0 else ("urgent" if jours <= 7 else ("attention" if jours <= 30 else "info"))
            result.append({
                "nom": doc.nom,
                "type_document": doc.type_document,
                "date_expiration": doc.date_expiration.isoformat(),
                "jours_restants": jours,
                "urgence": urgence,
            })

        return result


@service_factory("documents_notifications_interaction", tags={"famille", "notifications", "documents"})
def obtenir_service_documents_notifications() -> DocumentsNotificationsInteractionService:
    """Factory pour le service Documents → Notifications."""
    return DocumentsNotificationsInteractionService()
