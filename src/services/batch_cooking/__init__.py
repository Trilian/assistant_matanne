"""
Package batch_cooking - Gestion des sessions de préparation de repas en lot.

Ce package fournit:
- ServiceBatchCooking: Service principal pour le batch cooking
- Types Pydantic pour validation des données IA
- Constantes (robots, jours de la semaine)
- Fonctions utilitaires pures

Exemple d'utilisation:
    from src.services.batch_cooking import obtenir_service_batch_cooking
    
    service = obtenir_service_batch_cooking()
    session = service.creer_session(date_session=date.today(), recettes_ids=[1, 2, 3])
"""

# Service principal
from .service import (
    ServiceBatchCooking,
    BatchCookingService,  # Alias rétrocompatibilité
    obtenir_service_batch_cooking,
    get_batch_cooking_service,  # Alias rétrocompatibilité
)

# Types Pydantic
from .types import (
    EtapeBatchIA,
    SessionBatchIA,
    PreparationIA,
)

# Constantes
from .constantes import (
    JOURS_SEMAINE,
    ROBOTS_DISPONIBLES,
    ROBOTS_CUISINE,  # Alias
)

# Fonctions utilitaires
from .utils import (
    # Durées
    calculer_duree_totale_etapes,
    calculer_duree_parallele,
    calculer_duree_reelle,
    estimer_heure_fin,
    # Robots
    obtenir_info_robot,
    obtenir_nom_robot,
    obtenir_emoji_robot,
    est_robot_parallele,
    formater_liste_robots,
    filtrer_robots_paralleles,
    # Jours
    obtenir_nom_jour,
    obtenir_index_jour,
    formater_jours_batch,
    est_jour_batch,
    prochain_jour_batch,
    # Contexte
    construire_contexte_recette,
    construire_contexte_jules,
    # Session
    calculer_progression_session,
    calculer_temps_restant,
    # Préparations
    calculer_portions_restantes,
    est_preparation_expiree,
    jours_avant_expiration,
    est_preparation_a_risque,
    # Validation
    valider_jours_batch,
    valider_duree,
    valider_portions,
    valider_conservation,
)


__all__ = [
    # Service
    "ServiceBatchCooking",
    "BatchCookingService",
    "obtenir_service_batch_cooking",
    "get_batch_cooking_service",
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
