"""
Utilitaires du Calendrier Familial Unifié.

Ce module réexporte les éléments de:
- types.py: Dataclasses et enums
- converters.py: Fonctions de conversion
- aggregation.py: Agrégation des événements
- export.py: Export texte/HTML
"""

# Types et dataclasses
# Compatibilité: importer get_debut_semaine depuis shared
# Réexport de JOURS_SEMAINE pour compatibilité
from src.modules.shared.constantes import JOURS_SEMAINE, JOURS_SEMAINE_COURT
from src.modules.shared.date_utils import obtenir_debut_semaine as get_debut_semaine
from src.modules.shared.date_utils import obtenir_fin_semaine as get_fin_semaine

# Aggregation
from .aggregation import (
    agreger_evenements_jour,
    construire_semaine_calendrier,
    generer_taches_menage_semaine,
    get_jours_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
)

# Converters
from .converters import (
    convertir_activite_en_evenement,
    convertir_event_calendrier_en_evenement,
    convertir_repas_en_evenement,
    convertir_session_batch_en_evenement,
    convertir_tache_menage_en_evenement,
    creer_evenement_courses,
)

# Export
from .export import (
    generer_html_semaine_pour_impression,
    generer_texte_semaine_pour_impression,
)
from .types import (
    COULEUR_TYPE,
    EMOJI_TYPE,
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
)

__all__ = [
    # Types
    "TypeEvenement",
    "EMOJI_TYPE",
    "COULEUR_TYPE",
    "EvenementCalendrier",
    "JourCalendrier",
    "SemaineCalendrier",
    # Constantes
    "JOURS_SEMAINE",
    "JOURS_SEMAINE_COURT",
    # Converters
    "convertir_repas_en_evenement",
    "convertir_session_batch_en_evenement",
    "convertir_activite_en_evenement",
    "convertir_event_calendrier_en_evenement",
    "convertir_tache_menage_en_evenement",
    "creer_evenement_courses",
    # Aggregation
    "get_jours_semaine",
    "get_semaine_precedente",
    "get_semaine_suivante",
    "generer_taches_menage_semaine",
    "agreger_evenements_jour",
    "construire_semaine_calendrier",
    # Export
    "generer_texte_semaine_pour_impression",
    "generer_html_semaine_pour_impression",
    # Date utils (compatibilité)
    "get_debut_semaine",
    "get_fin_semaine",
]
