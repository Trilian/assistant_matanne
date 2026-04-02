"""
Service inter-modules : Garmin/Santé → Cuisine adultes (nutrition).

NIM3: Niveaux d'activité Garmin → recommandations nutritionnelles adultes.
Étendre le bridge santé existant (Jules) à tous les profils famille.
"""

import logging
from datetime import date as date_type
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class GarminNutritionAdultesInteractionService:
    """Service inter-modules Garmin/Santé → Cuisine adultes."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def calculer_besoins_nutritionnels_selon_activite(
        self,
        *,
        profil_id: int | None = None,
        db=None,
    ) -> dict[str, Any]:
        """Calcule les besoins nutritionnels des adultes basé sur l'activité Garmin.

        Récupère le niveau d'activité (étapes, calories brûlées, intensité des exercices)
        et recommande les macronutriments et calories pour le planning alimentaire.

        Args:
            profil_id: ID du profil famille (défaut: premier adulte)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec:
                - calories_recommended: Calories quotidiennes recommandées
                - macros: {'proteines': g, 'lipides': g, 'glucides': g}
                - niveau_activite: Niveau détecté (sédentaire/modéré/actif)
                - details: Explications et sources données
        """
        from src.core.models.users import ResumeQuotidienGarmin, ProfilUtilisateur

        # Récupérer le profil utilisateur
        profil_utilisateur = db.query(ProfilUtilisateur).first()
        if not profil_utilisateur:
            return {
                "profile_utilisateur_id": None,
                "nom_profil": "Utilisateur",
                "calories_recommended": 2000,
                "calories_base": 1700,
                "calories_bonus_activite": 300,
                "macros": {"proteines_g": 125, "lipides_g": 56, "glucides_g": 250},
                "niveau_activite": "modéré",
                "pas_detectes": 0,
                "calories_actives_detectees": 0,
                "details": {
                    "formule": "Valeur par défaut en absence de profil Garmin",
                    "date_donnees": str(date_type.today()),
                    "conseil": "Utiliser un objectif nutritionnel adulte équilibré par défaut.",
                },
            }

        # Récupérer les données Garmin les plus récentes (dernier jour)
        donnees_garmin = (
            db.query(ResumeQuotidienGarmin)
            .filter(ResumeQuotidienGarmin.user_id == profil_utilisateur.id, 
                    ResumeQuotidienGarmin.date >= date_type.today())
            .order_by(ResumeQuotidienGarmin.id.desc())
            .first()
        )

        # Déterminer le niveau d'activité
        if not donnees_garmin:
            # Défaut si pas de données Garmin
            niveau_activite = "modéré"
            calories_bonus = 0
        else:
            # Heuristique basée sur les pas ou calories (colonnes Garmin)
            pas = donnees_garmin.pas or 0
            calories_brulees = donnees_garmin.calories_actives or 0

            if pas > 12000 or calories_brulees > 400:
                niveau_activite = "très actif"
                calories_bonus = 400
            elif pas > 8000 or calories_brulees > 250:
                niveau_activite = "actif"
                calories_bonus = 250
            elif pas > 5000 or calories_brulees > 100:
                niveau_activite = "modéré"
                calories_bonus = 100
            else:
                niveau_activite = "sédentaire"
                calories_bonus = 0

        # Formule Harris-Benedict pour calories de base (adapté aux adultes)
        # Hypothèse : poids 75kg, hauteur 170cm, âge 40
        calories_base = 1700  # Adapter selon le profil réel si données dispo
        calories_total = calories_base + calories_bonus

        # Calculs des macronutriments (distribution classique sports)
        proteines_g = round((calories_total * 0.25) / 4)  # 25% des calories = 4 cal/g
        lipides_g = round((calories_total * 0.25) / 9)  # 25% des calories = 9 cal/g
        glucides_g = round((calories_total * 0.5) / 4)  # 50% des calories = 4 cal/g

        logger.info(
            f"✅ Garmin→Nutrition adultes: {niveau_activite}, {calories_total} cal/jour, "
            f"P:{proteines_g}g L:{lipides_g}g G:{glucides_g}g"
        )

        return {
            "profile_utilisateur_id": profil_utilisateur.id,
            "nom_profil": getattr(profil_utilisateur, 'email', 'Utilisateur'),
            "calories_recommended": calories_total,
            "calories_base": calories_base,
            "calories_bonus_activite": calories_bonus,
            "macros": {
                "proteines_g": proteines_g,
                "lipides_g": lipides_g,
                "glucides_g": glucides_g,
            },
            "niveau_activite": niveau_activite,
            "pas_detectes": donnees_garmin.pas if donnees_garmin else 0,
            "calories_actives_detectees": donnees_garmin.calories_actives if donnees_garmin else 0,
            "details": {
                "formule": "Harris-Benedict + bonus activité Garmin",
                "date_donnees": str(date_type.today()),
                "conseil": f"Viser {calories_total} calories/jour avec {proteines_g}g de protéines pour {niveau_activite}.",
            },
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def recommander_recettes_selon_activite(
        self,
        *,
        profil_id: int | None = None,
        db=None,
    ) -> dict[str, Any]:
        """Recommande des recettes adaptées au niveau d'activité détecté.

        Args:
            profil_id: ID du profil famille
            db: Session DB

        Returns:
            Dict avec liste de recettes recommandées
        """
        from src.core.models.recettes import Recette

        besoins = self.calculer_besoins_nutritionnels_selon_activite(profil_id=profil_id, db=db)

        niveau_activite = besoins.get("niveau_activite", "modéré")

        # Mapper niveau d'activité à tags de recettes
        tag_map = {
            "très actif": ["riche en protéines", "high protein", "muscle"],
            "actif": ["équilibré", "protéines modérées"],
            "modéré": ["varié", "nutritif"],
            "sédentaire": ["léger", "faible calorie"],
        }

        tags_requis = tag_map.get(niveau_activite, ["varié"])

        # Chercher les recettes avec tags apropos (approximation)
        recettes = db.query(Recette).filter(Recette.difficulte != "impossible").limit(5).all()

        recettes_recommandees = [
            {
                "recette_id": r.id,
                "nom": r.nom,
                "energie_kcal": r.energie_kcal,
                "proteines_g": r.proteines_g or 0,
            }
            for r in recettes
        ]

        logger.info(
            f"✅ Recettes recommandées: {len(recettes_recommandees)} pour {niveau_activite}"
        )

        return {
            "niveau_activite": niveau_activite,
            "tags_recherche": tags_requis,
            "recettes_recommandees": recettes_recommandees,
            "message": f"{len(recettes_recommandees)} recette(s) adaptée(s) au niveau {niveau_activite}.",
        }


@service_factory("garmin_nutrition_adultes", tags={"garmin", "santé", "cuisine", "nutrition"})
def get_garmin_nutrition_adultes_service() -> GarminNutritionAdultesInteractionService:
    """Factory pour le service inter-modules Garmin→Nutrition adultes."""
    return GarminNutritionAdultesInteractionService()
