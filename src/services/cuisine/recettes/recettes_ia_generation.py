"""Backward compatibility - imports from split modules.

Le mixin original a été divisé en deux fichiers :
- recettes_ia_suggestions.py : RecettesIASuggestionsMixin (generer_recettes_ia, generer_variantes_recette_ia)
- recettes_ia_versions.py : RecettesIAVersionsMixin (generer_version_bebe, generer_version_batch_cooking, generer_version_robot)

Ce fichier re-exporte le mixin combiné pour compatibilité ascendante.
"""

from .recettes_ia_suggestions import RecettesIASuggestionsMixin
from .recettes_ia_versions import RecettesIAVersionsMixin

__all__ = ["RecettesIAGenerationMixin"]


class RecettesIAGenerationMixin(RecettesIASuggestionsMixin, RecettesIAVersionsMixin):
    """Mixin combiné pour la génération IA de recettes.

    Combine RecettesIASuggestionsMixin (découverte/suggestions) et
    RecettesIAVersionsMixin (génération de versions avec persistance DB).
    """

    pass
