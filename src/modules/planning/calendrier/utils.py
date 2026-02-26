"""
DEPRECATED — Ce fichier façade est conservé pour compatibilité arrière.

Les imports doivent se faire directement depuis:
- .types (TypeEvenement, EvenementCalendrier, JourCalendrier, etc.)
- .converters (convertir_repas_en_evenement, etc.)
- .aggregation (construire_semaine_calendrier, etc.)
- .export (generer_texte_semaine_pour_impression, etc.)
- src.core.date_utils (get_debut_semaine, get_fin_semaine)
- src.core.constants (JOURS_SEMAINE, JOURS_SEMAINE_COURT)
"""

import warnings as _warnings

# Types et dataclasses
# Réexport de JOURS_SEMAINE pour compatibilité
from src.core.constants import JOURS_SEMAINE, JOURS_SEMAINE_COURT  # noqa: F401
from src.core.date_utils import obtenir_debut_semaine as get_debut_semaine  # noqa: F401
from src.core.date_utils import obtenir_fin_semaine as get_fin_semaine  # noqa: F401

# Aggregation
from .aggregation import (  # noqa: F401
    agreger_evenements_jour,
    construire_semaine_calendrier,
    generer_taches_menage_semaine,
    get_jours_semaine,
    get_semaine_precedente,
    get_semaine_suivante,
)

# Converters
from .converters import (  # noqa: F401
    convertir_activite_en_evenement,
    convertir_event_calendrier_en_evenement,
    convertir_repas_en_evenement,
    convertir_session_batch_en_evenement,
    convertir_tache_menage_en_evenement,
    creer_evenement_courses,
)

# Export
from .export import (  # noqa: F401
    generer_html_semaine_pour_impression,
    generer_texte_semaine_pour_impression,
)
from .types import (  # noqa: F401
    COULEUR_TYPE,
    EMOJI_TYPE,
    EvenementCalendrier,
    JourCalendrier,
    SemaineCalendrier,
    TypeEvenement,
)

_warnings.warn(
    "Importer depuis calendrier.utils est déprécié. "
    "Utilisez types, converters, aggregation ou export directement.",
    DeprecationWarning,
    stacklevel=2,
)
