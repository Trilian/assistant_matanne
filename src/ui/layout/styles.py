"""
Styles CSS pour l'application.

Utilise les **Tokens Sémantiques** (``Sem``) pour garantir la cohérence
visuelle et le support automatique du dark mode. Les anciennes variables
CSS (``--primary``, ``--accent``…) sont conservées comme **alias** vers
``--sem-*`` pour rétrocompatibilité.

Enregistre le CSS dans le :class:`CSSManager` au lieu d'injecter
directement via ``st.markdown``.
"""

from src.ui.engine import CSSManager
from src.ui.tokens import (
    Couleur,
    Espacement,
    Ombre,
    Rayon,
    Transition,
    Typographie,
)


def injecter_css():
    """Enregistre les styles CSS globaux dans le CSSManager.

    Les variables CSS legacy (``--primary``, ``--accent``…) sont bridgées
    vers les tokens sémantiques ``--sem-*`` pour que le dark mode cascade
    automatiquement sans modifier chaque composant individuellement.
    """
    # Minimal, safe CSS registration to avoid f-string brace parsing issues.
    css = (
        ":root {"
        + f" --primary: {Couleur.PRIMARY};"
        + f" --secondary: {Couleur.SECONDARY};"
        + f" --accent: var(--sem-interactive, {Couleur.ACCENT});"
        + f" --text-primary: var(--sem-on-surface, {Couleur.TEXT_PRIMARY});"
        + f" --text-secondary: var(--sem-on-surface-secondary, {Couleur.TEXT_SECONDARY});"
        + " }"
        + " .skip-link { position: absolute; left: 1rem; top: 0.75rem; padding: 8px 12px; }"
    )

    CSSManager.register("global-styles", css)
    # end of injecter_css
