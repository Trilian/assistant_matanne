"""
Utilitaires UI — sanitisation HTML, helpers de formatage.

Fournit des fonctions de sécurité pour l'injection HTML dans Streamlit.
"""

import html


def echapper_html(texte: str) -> str:
    """
    Échappe les caractères HTML dangereux pour prévenir les injections XSS.

    Utilise html.escape() pour convertir les caractères spéciaux (<, >, &, ", ')
    en entités HTML. À appeler sur tout texte utilisateur avant injection dans
    du HTML brut via st.markdown(unsafe_allow_html=True).

    Args:
        texte: Texte brut à sécuriser.

    Returns:
        Texte avec caractères HTML échappés.

    Example:
        safe = echapper_html(user_input)
        st.markdown(f"<div>{safe}</div>", unsafe_allow_html=True)
    """
    if not isinstance(texte, str):
        texte = str(texte)
    return html.escape(texte, quote=True)


__all__ = ["echapper_html"]
