"""
Package batch_cooking - Gestion des sessions de préparation de repas en lot.

Ce package fournit:
- ServiceBatchCooking: Service principal pour le batch cooking
- Types Pydantic pour validation des données IA
- Constantes (robots, jours de la semaine)
- Fonctions utilitaires pures

Imports paresseux (__getattr__) pour performance au démarrage.

Exemple d'utilisation:
    from src.services.cuisine.batch_cooking import obtenir_service_batch_cooking

    service = obtenir_service_batch_cooking()
"""

# ═══════════════════════════════════════════════════════════
# LAZY IMPORTS — Mapping symbol → (module, attr_name)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ─── Service ───
    "ServiceBatchCooking": (".service", "ServiceBatchCooking"),
    "obtenir_service_batch_cooking": (".service", "obtenir_service_batch_cooking"),
    # ─── Mixins ───
    "BatchCookingIAMixin": (".batch_cooking_ia", "BatchCookingIAMixin"),
    "BatchCookingStatsMixin": (".batch_cooking_stats", "BatchCookingStatsMixin"),
    # ─── Types ───
    "EtapeBatchIA": (".types", "EtapeBatchIA"),
    "SessionBatchIA": (".types", "SessionBatchIA"),
    "PreparationIA": (".types", "PreparationIA"),
    # ─── Constantes ───
    "JOURS_SEMAINE": (".constantes", "JOURS_SEMAINE"),
    "ROBOTS_DISPONIBLES": (".constantes", "ROBOTS_DISPONIBLES"),
    "ROBOTS_CUISINE": (".constantes", "ROBOTS_CUISINE"),
    # ─── Utilitaires Durées ───
    "calculer_duree_totale_etapes": (".utils", "calculer_duree_totale_etapes"),
    "calculer_duree_parallele": (".utils", "calculer_duree_parallele"),
    "calculer_duree_reelle": (".utils", "calculer_duree_reelle"),
    "estimer_heure_fin": (".utils", "estimer_heure_fin"),
    # ─── Utilitaires Robots ───
    "obtenir_info_robot": (".utils", "obtenir_info_robot"),
    "obtenir_nom_robot": (".utils", "obtenir_nom_robot"),
    "obtenir_emoji_robot": (".utils", "obtenir_emoji_robot"),
    "est_robot_parallele": (".utils", "est_robot_parallele"),
    "formater_liste_robots": (".utils", "formater_liste_robots"),
    "filtrer_robots_paralleles": (".utils", "filtrer_robots_paralleles"),
    # ─── Utilitaires Jours ───
    "obtenir_nom_jour": (".utils", "obtenir_nom_jour"),
    "obtenir_index_jour": (".utils", "obtenir_index_jour"),
    "formater_jours_batch": (".utils", "formater_jours_batch"),
    "est_jour_batch": (".utils", "est_jour_batch"),
    "prochain_jour_batch": (".utils", "prochain_jour_batch"),
    # ─── Utilitaires Contexte ───
    "construire_contexte_recette": (".utils", "construire_contexte_recette"),
    "construire_contexte_jules": (".utils", "construire_contexte_jules"),
    # ─── Utilitaires Session ───
    "calculer_progression_session": (".utils", "calculer_progression_session"),
    "calculer_temps_restant": (".utils", "calculer_temps_restant"),
    # ─── Utilitaires Préparations ───
    "calculer_portions_restantes": (".utils", "calculer_portions_restantes"),
    "est_preparation_expiree": (".utils", "est_preparation_expiree"),
    "jours_avant_expiration": (".utils", "jours_avant_expiration"),
    "est_preparation_a_risque": (".utils", "est_preparation_a_risque"),
    # ─── Utilitaires Validation ───
    "valider_jours_batch": (".utils", "valider_jours_batch"),
    "valider_duree": (".utils", "valider_duree"),
    "valider_portions": (".utils", "valider_portions"),
    "valider_conservation": (".utils", "valider_conservation"),
}


def __getattr__(name: str):
    """Lazy import pour performance au démarrage."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        import importlib

        mod = importlib.import_module(module_path, package=__name__)
        return getattr(mod, attr_name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
