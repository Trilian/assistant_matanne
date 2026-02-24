"""
Sidebar — DEPRECATED.

La navigation est désormais gérée par ``src.core.navigation`` via ``st.navigation()``.
Ce module est conservé pour la rétrocompatibilité des imports,
mais ne contient plus de logique active.

See Also:
    src/core/navigation.py — routing actif via st.navigation() + st.Page()
"""

import logging
import warnings

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# STUBS RÉTROCOMPATIBLES (deprecated)
# ═══════════════════════════════════════════════════════════

MODULES_MENU: dict = {}  # Remplacé par construire_pages() dans navigation.py


def afficher_sidebar() -> None:
    """DEPRECATED — La sidebar est rendue automatiquement par st.navigation()."""
    warnings.warn(
        "afficher_sidebar() est deprecated. La navigation est gérée par "
        "src.core.navigation.initialiser_navigation().",
        DeprecationWarning,
        stacklevel=2,
    )
    logger.warning("afficher_sidebar() appelé — cette fonction est deprecated.")
