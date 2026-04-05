"""
Service Notifications Maison — Push ntfy.sh pour rappels maison.

Évalue quotidiennement les conditions de rappel et envoie via ServiceNtfy.
Dédoublonnage via cache interne (dernière date d'envoi par entité).
"""

import logging
from datetime import date

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.monitoring import chronometre
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class RappelResult(BaseModel):
    """Résultat de l'évaluation des rappels."""

    rappels_envoyes: int = 0
    rappels_ignores: int = 0
    erreurs: list[str] = Field(default_factory=list)


class NotificationsMaisonService:
    """Évalue et envoie les rappels push maison via ntfy.sh."""

    def __init__(self):
        # Cache de dédoublonnage: {clé: date dernier envoi}
        self._derniers_envois: dict[str, date] = {}

    def _deja_envoye_aujourdhui(self, cle: str) -> bool:
        """Vérifie si un rappel a déjà été envoyé aujourd'hui."""
        return self._derniers_envois.get(cle) == date.today()

    def _marquer_envoye(self, cle: str) -> None:
        """Marque un rappel comme envoyé aujourd'hui."""
        self._derniers_envois[cle] = date.today()

    @chronometre("maison.rappels", seuil_alerte_ms=5000)
    @avec_gestion_erreurs(default_return=None)
    def evaluer_et_envoyer_rappels(self) -> RappelResult:
        """Évalue toutes les conditions et envoie les rappels pertinents."""
        result = RappelResult()

        # Charger le service ntfy
        try:
            from src.services.core.notifications import obtenir_service_ntfy, NotificationNtfy

            ntfy = obtenir_service_ntfy()
        except Exception as e:
            logger.error(f"Service ntfy indisponible: {e}")
            result.erreurs.append(f"ntfy indisponible: {e}")
            return result

        # 1. Entretien obligatoire en retard
        self._check_entretien_retard(ntfy, NotificationNtfy, result)

        # 2. Gel prévu
        self._check_gel(ntfy, NotificationNtfy, result)

        # 3. Cellier — articles périmés
        self._check_cellier(ntfy, NotificationNtfy, result)

        logger.info(
            f"Rappels maison: {result.rappels_envoyes} envoyés, "
            f"{result.rappels_ignores} ignorés"
        )
        return result

    def _check_entretien_retard(self, ntfy, NotificationNtfy, result: RappelResult) -> None:
        """Vérifie les tâches d'entretien en retard."""
        try:
            from src.core.decorators import avec_session_db
            from src.core.models import TacheEntretien

            @avec_session_db
            def _get_retards(db=None):
                today = date.today()
                return (
                    db.query(TacheEntretien)
                    .filter(
                        TacheEntretien.prochaine_fois < today,
                        TacheEntretien.fait.is_(False),
                    )
                    .limit(5)
                    .all()
                )

            for t in _get_retards():
                cle = f"retard_{t.id}"
                if self._deja_envoye_aujourdhui(cle):
                    result.rappels_ignores += 1
                    continue

                jours_retard = (date.today() - t.prochaine_fois).days
                notif = NotificationNtfy(
                    titre=f"🔧 {t.nom} en retard",
                    message=f"En retard de {jours_retard} jour(s).",
                    priorite=4 if jours_retard > 7 else 3,
                    tags=["wrench", "warning"],
                )
                r = ntfy.envoyer_sync(notif)
                if r.succes:
                    self._marquer_envoye(cle)
                    result.rappels_envoyes += 1
                else:
                    result.erreurs.append(f"Entretien {t.nom}: {r.message}")
        except Exception as e:
            result.erreurs.append(f"Entretien retard: {e}")

    def _check_gel(self, ntfy, NotificationNtfy, result: RappelResult) -> None:
        """Vérifie si du gel est prévu."""
        cle = "gel_jardin"
        if self._deja_envoye_aujourdhui(cle):
            result.rappels_ignores += 1
            return

        try:
            from src.services.integrations.weather import get_meteo_service

            service = get_meteo_service()
            previsions = service.get_previsions(nb_jours=2)
            if not previsions:
                return

            for prev in previsions[:2]:
                if prev.temperature_min <= 0:
                    notif = NotificationNtfy(
                        titre="❄️ Gel prévu — protéger les plantes",
                        message=f"Température min: {prev.temperature_min}°C le {prev.date}",
                        priorite=4,
                        tags=["snowflake", "seedling"],
                    )
                    r = ntfy.envoyer_sync(notif)
                    if r.succes:
                        self._marquer_envoye(cle)
                        result.rappels_envoyes += 1
                    break
        except Exception as e:
            result.erreurs.append(f"Gel: {e}")

    def _check_cellier(self, ntfy, NotificationNtfy, result: RappelResult) -> None:
        """Vérifie les articles périmés dans le cellier."""
        try:
            from src.services.maison import obtenir_cellier_crud_service

            service = obtenir_cellier_crud_service()
            perimes = service.get_alertes_peremption(jours_horizon=0)
            if not perimes:
                return

            cle = "cellier_perimes"
            if self._deja_envoye_aujourdhui(cle):
                result.rappels_ignores += 1
                return

            noms = [a.get("nom", "?") for a in perimes[:3]]
            notif = NotificationNtfy(
                titre=f"🗑️ {len(perimes)} article(s) périmé(s) dans le cellier",
                message=f"À jeter: {', '.join(noms)}",
                priorite=3,
                tags=["wastebasket", "warning"],
            )
            r = ntfy.envoyer_sync(notif)
            if r.succes:
                self._marquer_envoye(cle)
                result.rappels_envoyes += 1
        except Exception as e:
            result.erreurs.append(f"Cellier: {e}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("notifications_maison", tags={"maison", "notification"})
def obtenir_notifications_maison_service() -> NotificationsMaisonService:
    """Factory singleton pour le service notifications maison."""
    return NotificationsMaisonService()


def obtenir_service_notifications_maison() -> NotificationsMaisonService:
    """Alias français."""
    return obtenir_notifications_maison_service()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
obtenir_notifications_maison_service = obtenir_notifications_maison_service  # alias rétrocompatibilité 
