"""
Service pour les interactions inter-modules Energie × Cuisine.

IM5: Heures creuses → suggérer appareils (Cookeo, etc.)
"""

import logging

from src.core.decorators import avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class EnergiecuisineInteractionService:
    """Service pour les interactions Energie × Cuisine."""

    @avec_session_db
    def obtenir_suggestions_heures_creuses(self, db=None) -> dict:
        """Suggère les appareils à utiliser aux heures creuses (IM5).

        Récupère les plages d'heures creuses depuis la config énergie et suggère
        d'utiliser les appareils haute consommation à ces heures (Cookeo, etc.).

        Args:
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec plages d'heures creuses et appareils recommandés
        """
        from datetime import datetime, time

        try:
            # Configuration par défaut des heures creuses (France: 22h-6h)
            heures_creuses = {
                "debut": "22:00",
                "fin": "06:00",
                "jours": "tous",
                "economie_kwh": 40,  # % d'économie estimée
            }

            # Récupérer heure actuelle
            now = datetime.now()
            heure_actuelle = now.time()

            # Convertir les heures creuses en time objects
            debut_hc = datetime.strptime(heures_creuses["debut"], "%H:%M").time()
            fin_hc = datetime.strptime(heures_creuses["fin"], "%H:%M").time()

            # Vérifier si on est en heures creuses
            en_heures_creuses = (
                heure_actuelle >= debut_hc or heure_actuelle <= fin_hc
            )

            # Appareils recommandés pour les heures creuses
            appareils_recommandes = [
                {
                    "nom": "Cookeo / Autocuiseur",
                    "consommation_kwh": 2.5,
                    "temps_preparation_min": 45,
                    "economies_estimees_euros": 0.75,
                    "type": "cuisson",
                },
                {
                    "nom": "Four électrique",
                    "consommation_kwh": 2.0,
                    "temps_preparation_min": 60,
                    "economies_estimees_euros": 0.60,
                    "type": "cuisson",
                },
                {
                    "nom": "Lave-vaisselle",
                    "consommation_kwh": 1.8,
                    "temps_preparation_min": 120,
                    "economies_estimees_euros": 0.54,
                    "type": "entretien",
                },
                {
                    "nom": "Lave-linge",
                    "consommation_kwh": 1.5,
                    "temps_preparation_min": 90,
                    "economies_estimees_euros": 0.45,
                    "type": "entretien",
                },
            ]

            # Message personnalisé selon l'heure
            if en_heures_creuses:
                periode_texte = f"Heures creuses jusqu'à {heures_creuses['fin']}"
                recommandation = "C'est le moment idéal d'utiliser ces appareils !"
            else:
                prochaines_hc = heures_creuses["debut"]
                periode_texte = (
                    f"Prochaines heures creuses à {prochaines_hc} "
                    f"(économies jusqu'à {heures_creuses['fin']})"
                )
                recommandation = f"Programmez vos appareils pour {prochaines_hc}"

            return {
                "en_heures_creuses": en_heures_creuses,
                "plage": {
                    "debut": heures_creuses["debut"],
                    "fin": heures_creuses["fin"],
                },
                "periode_texte": periode_texte,
                "recommandation": recommandation,
                "appareils_recommandes": appareils_recommandes,
                "economie_potentielle_percent": heures_creuses["economie_kwh"],
                "heure_actuelle": heure_actuelle.strftime("%H:%M"),
            }

        except Exception as e:
            logger.error(f"Erreur suggestions heures creuses: {e}")
            return {"error": str(e)}


@service_factory("energie_cuisine_interaction", tags={"energie", "cuisine"})
def obtenir_service_energie_cuisine_interaction() -> EnergiecuisineInteractionService:
    """Factory pour le service Energie × Cuisine."""
    return EnergiecuisineInteractionService()
