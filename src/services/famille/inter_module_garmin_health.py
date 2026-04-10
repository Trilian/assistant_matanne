"""
Service pour les interactions inter-modules Garmin × Planning/Famille.

IM6: Calories brûlées → ajustement macros
IM7: Dashboard santé famille
"""

import logging

from src.core.decorators import avec_cache, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class GarminHealthInteractionService:
    """Service pour les interactions Garmin × Nutrition/Santé famille."""

    @avec_cache(ttl=3600)
    @avec_session_db
    def calculer_macro_nutrition_ajustees(
        self,
        user_id: str,
        date_jour: str = None,
        db=None,
    ) -> dict:
        """Ajuste les macros du planning en fonction des calories brûlées Garmin (IM6).

        Récupère les données Garmin (calories brûlées) et ajuste les recommandations
        nutritionnelles du planning du jour.

        Args:
            user_id: ID de l'utilisateur
            date_jour: Date (ISO format, défaut: aujourd'hui)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec macros ajustées et recommandations
        """
        from datetime import date as date_type
        from datetime import datetime

        from sqlalchemy import func

        try:
            if not date_jour:
                date_jour = datetime.now().date()
            else:
                date_jour = datetime.fromisoformat(date_jour).date()

            # Récupérer les données Garmin (simulation)
            calories_brulees = 450  # Simulation: 450 kcal brûlées
            # En production: db.query(GarminSync).filter(...).first()

            # Macros de base recommandées
            calories_base = 2000
            calories_cible = calories_base + calories_brulees  # Ajouter les calories brûlées

            # Calcul des macros proportionnelles
            proteines_g = 50 + (calories_brulees / 2000 * 10)  # +50g base +%
            lipides_g = 65 + (calories_brulees / 2000 * 5)
            glucides_g = 300 + (calories_brulees / 2000 * 30)

            return {
                "date": str(date_jour),
                "calories_brulees_garmin": calories_brulees,
                "calories_cible": int(calories_cible),
                "calories_base": calories_base,
                "macros_ajustees": {
                    "proteines_g": round(proteines_g, 1),
                    "lipides_g": round(lipides_g, 1),
                    "glucides_g": round(glucides_g, 1),
                },
                "ajustement_message": (
                    f"Vous avez brûlé +{calories_brulees} kcal → "
                    f"Objectif du jour: {int(calories_cible)} kcal"
                ),
                "recommandation": (
                    f"Ajustez le dîner: +{int(calories_brulees / 2)} kcal pour compenser "
                    "(protéines et glucides complexes)"
                ),
            }

        except Exception as e:
            logger.error(f"Erreur calcul macro nutrition: {e}")
            return {"error": str(e)}

    @avec_cache(ttl=1800)
    @avec_session_db
    def calculer_dashboard_sante_famille(
        self,
        user_id: str,
        db=None,
    ) -> dict:
        """Génère le dashboard santé famille (IM7).

        Agrège les données de:
        - Activité Garmin adultes
        - Sommeil Garmin adultes
        - Nutrition Jules
        - Score bien-être global

        Args:
            user_id: ID de l'utilisateur principal
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec métriques santé famille consolidées
        """
        from datetime import datetime, timedelta

        try:
            # Simulation des données Garmin (en production: depuis DB/API)
            activite_adultes = {
                "pas_jour": 8500,
                "calories_brulees": 450,
                "temps_activite_min": 65,
                "zones_cardio": {
                    "repos": 480,
                    "faible": 120,
                    "modere": 45,
                    "intense": 15,
                },
            }

            sommeil_adultes = {
                "duree_h": 7.5,
                "qualite_pct": 85,
                "profond_min": 60,
                "rem_min": 90,
            }

            nutrition_jules = {
                "calories_ingestion": 800,
                "calories_cible": 850,
                "proteines_g": 22,
                "textures_variees": True,
                "allergenes_evites": True,
            }

            # Calcul du score bien-être global
            score_activite = min(100, (activite_adultes["pas_jour"] / 10000) * 100)
            score_sommeil = sommeil_adultes["qualite_pct"]
            score_nutrition_famille = (
                (nutrition_jules["calories_ingestion"] / nutrition_jules["calories_cible"]) * 100
                if nutrition_jules["calories_cible"] > 0
                else 0
            )

            bien_etre_global = (score_activite + score_sommeil + score_nutrition_famille) / 3

            return {
                "date": datetime.now().date().isoformat(),
                "activite_adultes": activite_adultes,
                "sommeil_adultes": sommeil_adultes,
                "nutrition_jules": nutrition_jules,
                "scores": {
                    "activite_pct": round(score_activite, 1),
                    "sommeil_pct": round(score_sommeil, 1),
                    "nutrition_pct": round(score_nutrition_famille, 1),
                    "bien_etre_global_pct": round(bien_etre_global, 1),
                },
                "resume": {
                    "activite": (
                        "✅ Excellente"
                        if score_activite >= 80
                        else "🟡 Bonne"
                        if score_activite >= 60
                        else "⚠️ À améliorer"
                    ),
                    "sommeil": (
                        "✅ Bon"
                        if score_sommeil >= 80
                        else "🟡 Acceptable"
                        if score_sommeil >= 60
                        else "⚠️ Insuffisant"
                    ),
                    "nutrition": (
                        "✅ Équilibrée"
                        if score_nutrition_famille >= 90
                        else "🟡 Acceptable"
                        if score_nutrition_famille >= 80
                        else "⚠️ À vérifier"
                    ),
                },
                "tendance_semaine": [
                    {"jour": "lun", "score": 78},
                    {"jour": "mar", "score": 82},
                    {"jour": "mer", "score": 80},
                    {"jour": "jeu", "score": 85},
                    {"jour": "ven", "score": 88},
                    {"jour": "sam", "score": 90},
                    {"jour": "dim", "score": round(bien_etre_global, 1)},
                ],
            }

        except Exception as e:
            logger.error(f"Erreur dashboard santé: {e}")
            return {"error": str(e)}


@service_factory("garmin_health_interaction", tags={"garmin", "nutrition", "famille"})
def obtenir_service_garmin_health_interaction() -> GarminHealthInteractionService:
    """Factory pour le service Garmin × Santé."""
    return GarminHealthInteractionService()
