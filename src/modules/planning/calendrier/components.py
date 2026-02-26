"""
DEPRECATED — Ce fichier façade est conservé pour compatibilité arrière.

Les imports doivent se faire directement depuis:
- .components_jour
- .components_semaine
- .components_formulaire
"""

# Re-exports pour compatibilité arrière (tests existants)
import warnings as _warnings

from .components_formulaire import (  # noqa: F401
    afficher_formulaire_ajout_event,
    afficher_legende,
    afficher_navigation_semaine,
)
from .components_jour import (  # noqa: F401
    afficher_cellule_jour,
    afficher_jour_calendrier,
    afficher_jour_sortable,
)
from .components_semaine import (  # noqa: F401
    afficher_actions_rapides,
    afficher_modal_impression,
    afficher_stats_semaine,
    afficher_vue_semaine_grille,
    afficher_vue_semaine_liste,
)

_warnings.warn(
    "Importer depuis calendrier.components est déprécié. "
    "Utilisez components_jour, components_semaine ou components_formulaire directement.",
    DeprecationWarning,
    stacklevel=2,
)
