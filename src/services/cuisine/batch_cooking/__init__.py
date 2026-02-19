"""
Package batch_cooking - Gestion des sessions de préparation de repas en lot.

Ce package fournit:
- ServiceBatchCooking: Service principal pour le batch cooking
- Types Pydantic pour validation des données IA
- Constantes (robots, jours de la semaine)
- Fonctions utilitaires pures

Exemple d'utilisation:
    from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking

    service = obtenir_service_batch_cooking()
    session = service.creer_session(date_session=date.today(), recettes_ids=[1, 2, 3])
"""

# Service principal et mixins
# Constantes
from .batch_cooking_ia import BatchCookingIAMixin
from .batch_cooking_stats import BatchCookingStatsMixin
from .constantes import (
    JOURS_SEMAINE,
    ROBOTS_CUISINE,  # Alias
    ROBOTS_DISPONIBLES,
)
from .service import (
    BatchCookingService,  # Alias rétrocompatibilité
    ServiceBatchCooking,
    get_batch_cooking_service,  # Alias rétrocompatibilité
    obtenir_service_batch_cooking,
)

# Types Pydantic
from .types import (
    EtapeBatchIA,
    PreparationIA,
    SessionBatchIA,
)

# Fonctions utilitaires
from .utils import (
    calculer_duree_parallele,
    calculer_duree_reelle,
    # Durées
    calculer_duree_totale_etapes,
    # Préparations
    calculer_portions_restantes,
    # Session
    calculer_progression_session,
    calculer_temps_restant,
    construire_contexte_jules,
    # Contexte
    construire_contexte_recette,
    est_jour_batch,
    est_preparation_a_risque,
    est_preparation_expiree,
    est_robot_parallele,
    estimer_heure_fin,
    filtrer_robots_paralleles,
    formater_jours_batch,
    formater_liste_robots,
    jours_avant_expiration,
    obtenir_emoji_robot,
    obtenir_index_jour,
    # Robots
    obtenir_info_robot,
    # Jours
    obtenir_nom_jour,
    obtenir_nom_robot,
    prochain_jour_batch,
    valider_conservation,
    valider_duree,
    # Validation
    valider_jours_batch,
    valider_portions,
)

__all__ = [
    # Service
    "ServiceBatchCooking",
    "BatchCookingService",
    "obtenir_service_batch_cooking",
    "get_batch_cooking_service",
    # Mixins
    "BatchCookingIAMixin",
    "BatchCookingStatsMixin",
    # Types
    "EtapeBatchIA",
    "SessionBatchIA",
    "PreparationIA",
    # Constantes
    "JOURS_SEMAINE",
    "ROBOTS_DISPONIBLES",
    "ROBOTS_CUISINE",
    # Utilitaires - Durées
    "calculer_duree_totale_etapes",
    "calculer_duree_parallele",
    "calculer_duree_reelle",
    "estimer_heure_fin",
    # Utilitaires - Robots
    "obtenir_info_robot",
    "obtenir_nom_robot",
    "obtenir_emoji_robot",
    "est_robot_parallele",
    "formater_liste_robots",
    "filtrer_robots_paralleles",
    # Utilitaires - Jours
    "obtenir_nom_jour",
    "obtenir_index_jour",
    "formater_jours_batch",
    "est_jour_batch",
    "prochain_jour_batch",
    # Utilitaires - Contexte
    "construire_contexte_recette",
    "construire_contexte_jules",
    # Utilitaires - Session
    "calculer_progression_session",
    "calculer_temps_restant",
    # Utilitaires - Préparations
    "calculer_portions_restantes",
    "est_preparation_expiree",
    "jours_avant_expiration",
    "est_preparation_a_risque",
    # Utilitaires - Validation
    "valider_jours_batch",
    "valider_duree",
    "valider_portions",
    "valider_conservation",
]
