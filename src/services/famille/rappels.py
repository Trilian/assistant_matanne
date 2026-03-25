"""
Service Rappels Famille — Évaluation et envoi de rappels intelligents.

Rappels supportés :
- Anniversaires (J-7, J-1 configurables)
- Documents expirants (J-30 info, J-7 warning, J-1 danger)
- Fermetures crèche (J-3)
- Jours fériés / ponts (J-5)
- Jalons OMS de Jules (mensuel)
"""

import logging
from datetime import date, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.monitoring import chronometre
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Stockage en mémoire des rappels déjà envoyés (clé: "type:ref:date")
_rappels_envoyes: set[str] = set()


class ServiceRappelsFamille:
    """Service de rappels intelligents pour la famille."""

    @chronometre(nom="rappels.evaluer", seuil_alerte_ms=3000)
    @avec_gestion_erreurs(default_return=[])
    def evaluer_rappels(self) -> list[dict[str, Any]]:
        """Évalue tous les rappels pertinents du jour."""
        aujourd_hui = date.today()
        rappels: list[dict[str, Any]] = []

        rappels.extend(self._rappels_anniversaires(aujourd_hui))
        rappels.extend(self._rappels_documents(aujourd_hui))
        rappels.extend(self._rappels_creche(aujourd_hui))
        rappels.extend(self._rappels_feries(aujourd_hui))
        rappels.extend(self._rappels_jalons_jules(aujourd_hui))

        # Trier par priorité (danger > warning > info)
        priorite_ordre = {"danger": 0, "warning": 1, "info": 2}
        rappels.sort(key=lambda r: priorite_ordre.get(r.get("priorite", "info"), 2))

        return rappels

    @avec_gestion_erreurs(default_return=0)
    def envoyer_rappels_du_jour(self) -> int:
        """Évalue les rappels et les envoie via push (ntfy)."""
        rappels = self.evaluer_rappels()
        nb_envoyes = 0

        for rappel in rappels:
            cle = f"{rappel['type']}:{rappel.get('date_cible', '')}:{date.today().isoformat()}"
            if cle in _rappels_envoyes:
                continue

            try:
                self._envoyer_push(rappel)
                _rappels_envoyes.add(cle)
                nb_envoyes += 1
            except Exception as e:
                logger.warning("Erreur envoi rappel %s: %s", rappel["type"], e)

        return nb_envoyes

    # ═══════════════════════════════════════════════════════════
    # SOURCES DE RAPPELS
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def _rappels_anniversaires(
        self, aujourd_hui: date, db=None  # noqa: ANN001
    ) -> list[dict[str, Any]]:
        """Rappels d'anniversaires basés sur rappel_jours_avant JSONB."""
        if db is None:
            return []

        from src.core.models import AnniversaireFamille

        items = (
            db.query(AnniversaireFamille)
            .filter(AnniversaireFamille.actif == True)  # noqa: E712
            .all()
        )
        rappels = []
        for a in items:
            jours_restants = a.jours_restants
            if jours_restants is None:
                continue

            seuils = a.rappel_jours_avant or [7, 1, 0]
            if jours_restants in seuils:
                priorite = "danger" if jours_restants <= 1 else ("warning" if jours_restants <= 3 else "info")
                rappels.append({
                    "type": "anniversaire",
                    "message": f"🎂 Anniversaire de {a.nom_personne} dans {jours_restants} jour(s) ({a.age + 1 if a.age else '?'} ans)",
                    "priorite": priorite,
                    "date_cible": a.prochain_anniversaire.isoformat() if a.prochain_anniversaire else None,
                    "jours_restants": jours_restants,
                    "click_url": "/famille/anniversaires",
                })

        return rappels

    def _rappels_documents(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Rappels documents expirants (J-30 info, J-7 warning, J-1 danger)."""
        try:
            from src.services.famille.documents import obtenir_service_documents

            service = obtenir_service_documents()
            alertes = service.obtenir_alertes_expiration(jours=30)
            if not alertes:
                return []

            rappels = []
            seuils_rappel = [30, 7, 1]
            for doc in alertes:
                jours = doc.get("jours_avant_expiration", 30)
                if jours in seuils_rappel or jours <= 1:
                    if jours <= 1:
                        priorite = "danger"
                    elif jours <= 7:
                        priorite = "warning"
                    else:
                        priorite = "info"
                    rappels.append({
                        "type": "document",
                        "message": f"📄 {doc.get('titre', 'Document')} expire dans {jours} jour(s)",
                        "priorite": priorite,
                        "date_cible": doc.get("date_expiration"),
                        "jours_restants": jours,
                        "click_url": "/famille/documents",
                    })
            return rappels
        except Exception as e:
            logger.warning("Erreur rappels documents: %s", e)
            return []

    def _rappels_creche(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Rappels fermetures crèche dans les 3 prochains jours."""
        try:
            from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

            service = obtenir_service_jours_speciaux()
            fermetures = service.fermetures_creche(aujourd_hui.year)
            limite = aujourd_hui + timedelta(days=3)

            rappels = []
            for f in fermetures:
                if aujourd_hui <= f.date_jour <= limite:
                    jours = (f.date_jour - aujourd_hui).days
                    rappels.append({
                        "type": "creche",
                        "message": f"🏫 {f.nom} — {f.date_jour.strftime('%A %d/%m')}",
                        "priorite": "warning" if jours <= 1 else "info",
                        "date_cible": f.date_jour.isoformat(),
                        "jours_restants": jours,
                        "click_url": "/famille",
                    })
            return rappels
        except Exception as e:
            logger.warning("Erreur rappels crèche: %s", e)
            return []

    def _rappels_feries(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Rappels jours fériés / ponts dans les 5 prochains jours."""
        try:
            from src.services.famille.jours_speciaux import obtenir_service_jours_speciaux

            service = obtenir_service_jours_speciaux()
            prochains = service.prochains_jours_speciaux(nb=10)
            limite = aujourd_hui + timedelta(days=5)

            rappels = []
            for j in prochains:
                if j.type in ("ferie", "pont") and aujourd_hui <= j.date_jour <= limite:
                    jours = (j.date_jour - aujourd_hui).days
                    rappels.append({
                        "type": "jour_special",
                        "message": f"🏖️ {j.nom} — {j.date_jour.strftime('%A %d/%m')}",
                        "priorite": "info",
                        "date_cible": j.date_jour.isoformat(),
                        "jours_restants": jours,
                        "click_url": "/famille/activites",
                    })
            return rappels
        except Exception as e:
            logger.warning("Erreur rappels fériés: %s", e)
            return []

    def _rappels_jalons_jules(self, aujourd_hui: date) -> list[dict[str, Any]]:
        """Rappels jalons OMS attendus pour l'âge de Jules."""
        try:
            from src.services.famille.contexte import obtenir_service_contexte_familial
            from src.services.famille.jules import obtenir_service_jules

            jules_service = obtenir_service_jules()
            date_naissance = jules_service.get_date_naissance_jules()
            if not date_naissance:
                return []

            age_mois = (aujourd_hui - date_naissance).days // 30

            contexte_service = obtenir_service_contexte_familial()
            jalons = contexte_service._prochains_jalons_oms(age_mois)

            if jalons:
                return [{
                    "type": "jalon_jules",
                    "message": f"👶 Jules ({age_mois} mois) : jalon attendu — {jalons[0]}",
                    "priorite": "info",
                    "date_cible": None,
                    "jours_restants": None,
                    "click_url": "/famille/jules",
                }]
            return []
        except Exception as e:
            logger.warning("Erreur rappels jalons Jules: %s", e)
            return []

    # ═══════════════════════════════════════════════════════════
    # HELPER PUSH
    # ═══════════════════════════════════════════════════════════

    def _envoyer_push(self, rappel: dict[str, Any]) -> None:
        """Envoie un rappel via ntfy.sh."""
        try:
            from src.services.integrations.ntfy import obtenir_service_ntfy

            service = obtenir_service_ntfy()
            priorite_map = {"danger": 5, "warning": 3, "info": 2}
            service.envoyer(
                titre=f"Rappel Famille — {rappel['type']}",
                message=rappel["message"],
                priorite=priorite_map.get(rappel.get("priorite", "info"), 2),
                click_url=rappel.get("click_url"),
            )
        except Exception as e:
            logger.warning("Push ntfy non disponible: %s", e)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("rappels_famille", tags={"famille", "rappels"})
def obtenir_service_rappels_famille() -> ServiceRappelsFamille:
    """Factory singleton pour ServiceRappelsFamille."""
    return ServiceRappelsFamille()


# Alias anglais
get_rappels_famille_service = obtenir_service_rappels_famille
