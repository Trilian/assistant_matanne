"""
Module Scan Factures — REDIRECT vers src.modules.utilitaires.scan_factures.

Ce fichier existait en doublon dans maison/ et utilitaires/.
La version de référence est dans utilitaires/. Ce stub conserve
le point d'entrée ``app()`` pour compatibilité ascendante.

Voir: src/modules/utilitaires/scan_factures.py
"""

import warnings

warnings.warn(
    "src.modules.maison.scan_factures est déprécié. "
    "Utilisez src.modules.utilitaires.scan_factures à la place.",
    DeprecationWarning,
    stacklevel=2,
)

from src.modules.utilitaires.scan_factures import app  # noqa: F401, E402

__all__ = ["app"]
