"""
UI Components - Atoms (composants de base)
badge, etat_vide, carte_metrique, separateur, boite_info, boule_loto

Implémentés avec StyleSheet pour la déduplication CSS
et échappement HTML manuel pour la sécurité XSS.

Note: Pour des métriques plus avancées avec icônes et liens,
utilisez carte_metrique_avancee depuis src.ui.components.metrics
"""

from __future__ import annotations

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.registry import composant_ui
from src.ui.tokens import (
    Couleur,
    Espacement,
    Ombre,
    Rayon,
    Typographie,
    Variante,
)
from src.ui.tokens_semantic import Sem
from src.ui.utils import echapper_html


# ── Helper pour tokens sémantiques variantes ──────────────
def _obtenir_sem_variante(variante: Variante) -> tuple[str, str, str]:
    """Retourne (background, text, border) en tokens sémantiques.

    Args:
        variante: Variante sémantique.

    Returns:
        Tuple (couleur_fond, couleur_texte, couleur_bordure) avec Sem tokens.
    """
    _MAP: dict[Variante, tuple[str, str, str]] = {
        Variante.SUCCESS: (Sem.SUCCESS_SUBTLE, Sem.ON_SUCCESS, Sem.SUCCESS),
        Variante.WARNING: (Sem.WARNING_SUBTLE, Sem.ON_WARNING, Sem.WARNING),
        Variante.DANGER: (Sem.DANGER_SUBTLE, Sem.ON_DANGER, Sem.DANGER),
        Variante.INFO: (Sem.INFO_SUBTLE, Sem.ON_INFO, Sem.INFO),
        Variante.NEUTRAL: (Sem.SURFACE_ALT, Sem.ON_SURFACE_SECONDARY, Sem.BORDER),
        Variante.ACCENT: (Sem.INTERACTIVE, Sem.ON_INTERACTIVE, Sem.INTERACTIVE),
    }
    return _MAP.get(variante, _MAP[Variante.NEUTRAL])


# ── Styles de badges pré-définis par variante ─────────────
_BADGE_BASE = (
    "display: inline-flex; align-items: center; "
    f"padding: {Espacement.XS} 0.75rem; "
    f"border-radius: {Rayon.PILL}; "
    f"font-size: {Typographie.BODY_SM}; font-weight: 600; "
    "line-height: 1.4;"
)

_BADGE_STYLES: dict[str, str] = {
    "success": f"{_BADGE_BASE} background: {Sem.SUCCESS_SUBTLE}; color: {Sem.ON_SUCCESS}; border: 1px solid {Sem.SUCCESS};",
    "warning": f"{_BADGE_BASE} background: {Sem.WARNING_SUBTLE}; color: {Sem.ON_WARNING}; border: 1px solid {Sem.WARNING};",
    "danger": f"{_BADGE_BASE} background: {Sem.DANGER_SUBTLE}; color: {Sem.ON_DANGER}; border: 1px solid {Sem.DANGER};",
    "info": f"{_BADGE_BASE} background: {Sem.INFO_SUBTLE}; color: {Sem.ON_INFO}; border: 1px solid {Sem.INFO};",
    "neutral": f"{_BADGE_BASE} background: {Sem.SURFACE_ALT}; color: {Sem.ON_SURFACE}; border: 1px solid {Sem.BORDER_SUBTLE};",
    "accent": f"{_BADGE_BASE} background: {Sem.INTERACTIVE}; color: {Sem.ON_INTERACTIVE}; border: 1px solid {Sem.INTERACTIVE};",
}


@composant_ui(
    "atoms",
    exemple='badge_html("Actif", variante=Variante.SUCCESS)',
    tags=("badge", "html", "pure"),
)
def badge_html(
    texte: str,
    variante: Variante | None = None,
    couleur: str | None = None,
) -> str:
    """Génère le HTML d'un badge coloré (fonction pure, testable).

    Args:
        texte: Texte du badge
        variante: Variante sémantique
        couleur: Couleur brute (hex) — déprécié, préférer ``variante``

    Returns:
        Chaîne HTML du badge.
    """
    safe_text = echapper_html(texte)

    if couleur and variante is None:
        return (
            f'<span role="status" aria-label="{safe_text}" style="display: inline-flex; background: {couleur}; color: {Sem.ON_INTERACTIVE}; '
            f"padding: {Espacement.XS} 0.75rem; border-radius: {Rayon.PILL}; "
            f'font-size: {Typographie.BODY_SM}; font-weight: 600;">{safe_text}</span>'
        )
    else:
        variant_name = variante.value if variante else "success"
        style = _BADGE_STYLES.get(variant_name, _BADGE_STYLES["success"])
        return f'<span role="status" aria-label="{safe_text}" style="{style}">{safe_text}</span>'


@composant_ui("atoms", exemple='badge("Actif", variante=Variante.SUCCESS)', tags=["badge", "label"])
def badge(
    texte: str,
    variante: Variante | None = None,
    couleur: str | None = None,
) -> None:
    """
    Badge coloré avec variante sémantique.

    Args:
        texte: Texte du badge
        variante: Variante sémantique (SUCCESS, WARNING, DANGER, INFO, NEUTRAL, ACCENT)
        couleur: Couleur brute (hex) — déprécié, préférer ``variante``

    Example:
        badge("Actif", variante=Variante.SUCCESS)
        badge("Urgent", variante=Variante.DANGER)
    """
    st.markdown(badge_html(texte, variante, couleur), unsafe_allow_html=True)


@composant_ui("atoms", exemple='etat_vide("Aucune recette", "🍽️")', tags=["empty", "placeholder"])
def etat_vide(message: str, icone: str = "📭", sous_texte: str | None = None):
    """
    État vide centré.

    Args:
        message: Message principal
        icone: Icône (emoji)
        sous_texte: Texte secondaire

    Example:
        etat_vide("Aucune recette", "🍽️", "Ajoutez-en une")
    """
    container_cls = StyleSheet.create_class(
        {
            "display": "flex",
            "flex-direction": "column",
            "align-items": "center",
            "padding": Espacement.XXL,
            "color": Sem.ON_SURFACE_SECONDARY,
            "text-align": "center",
        }
    )

    safe_icone = echapper_html(icone)
    safe_message = echapper_html(message)

    sous_texte_html = ""
    if sous_texte:
        safe_sous_texte = echapper_html(sous_texte)
        sous_texte_html = (
            f'<div style="font-size: {Typographie.BODY}; margin-top: {Espacement.SM};">'
            f"{safe_sous_texte}</div>"
        )

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}" role="status" aria-label="{safe_message}">'
        f'<div style="font-size: {Typographie.DISPLAY};" aria-hidden="true">{safe_icone}</div>'
        f'<div style="font-size: {Typographie.H3}; font-weight: 500; margin-top: {Espacement.MD};">'
        f"{safe_message}</div>"
        f"{sous_texte_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


@composant_ui("atoms", exemple='carte_metrique("Total", "42", "+5")', tags=["metric", "kpi"])
def carte_metrique(
    label: str,
    valeur: str,
    delta: str | None = None,
    couleur: str = Sem.SURFACE,
):
    """
    Carte métrique simple.

    Pour des métriques plus avancées (avec icône, lien module, gradient),
    préférez `carte_metrique_avancee` de src.ui.components.metrics.

    Args:
        label: Label métrique
        valeur: Valeur
        delta: Variation (optionnel)
        couleur: Couleur fond

    See Also:
        carte_metrique_avancee: Version avancée avec plus d'options
    """
    card_cls = StyleSheet.create_class(
        {
            "background": couleur,
            "padding": Espacement.LG,
            "border-radius": Rayon.LG,
            "box-shadow": Ombre.SM,
        }
    )

    safe_label = echapper_html(label)
    safe_valeur = echapper_html(valeur)

    # Delta optionnel
    delta_html = ""
    if delta:
        delta_str = str(delta).strip()
        if delta_str.startswith("-") or delta_str.startswith("↓"):
            delta_couleur = Sem.DANGER
        elif delta_str in ("0", "+0"):
            delta_couleur = Sem.ON_SURFACE_MUTED
        else:
            delta_couleur = Sem.SUCCESS
        safe_delta = echapper_html(delta)
        delta_html = (
            f'<div style="font-size: {Typographie.BODY_SM}; color: {delta_couleur}; '
            f'margin-top: {Espacement.XS};">{safe_delta}</div>'
        )

    StyleSheet.inject()
    st.markdown(
        f'<div class="{card_cls}" role="group" aria-label="{safe_label}: {safe_valeur}">'
        f'<div style="font-size: {Typographie.BODY_SM}; font-weight: 500; '
        f'color: {Sem.ON_SURFACE_SECONDARY};">{safe_label}</div>'
        f'<div style="font-size: {Typographie.H2}; font-weight: bold; '
        f'margin-top: {Espacement.SM};">{safe_valeur}</div>'
        f"{delta_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


@composant_ui("atoms", exemple='separateur("OU")', tags=["divider", "separator"])
def separateur(texte: str | None = None):
    """
    Séparateur avec texte optionnel

    Example:
        separateur("OU")
    """
    if texte:
        st.markdown(
            f'<div style="text-align: center; margin: {Espacement.LG} 0;">'
            f'<span style="padding: 0 {Espacement.MD}; '
            f"background: {Sem.SURFACE}; "
            f'position: relative; top: -0.75rem;">{echapper_html(texte)}</span>'
            f'<hr style="margin-top: -{Espacement.LG}; '
            f'border: 1px solid {Sem.BORDER_SUBTLE};">'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("---")


@composant_ui(
    "atoms",
    exemple='boite_info_html("Astuce", "Ctrl+S", "💡")',
    tags=("info", "callout", "html", "pure"),
)
def boite_info_html(
    titre: str,
    contenu: str,
    icone: str = "ℹ️",
    variante: Variante = Variante.INFO,
) -> str:
    """Génère le HTML d'une boîte d'information (fonction pure, testable).

    Args:
        titre: Titre de la boîte
        contenu: Contenu textuel
        icone: Icône emoji
        variante: Variante visuelle

    Returns:
        Chaîne HTML de la boîte info.
    """
    bg, text_color, border_color = _obtenir_sem_variante(variante)
    safe_titre = echapper_html(f"{icone} {titre}")
    safe_contenu = echapper_html(contenu)

    style = (
        f"background: {bg}; border-left: 4px solid {border_color}; "
        f"padding: {Espacement.MD}; border-radius: {Rayon.SM}; "
        f"margin: {Espacement.MD} 0;"
    )

    return (
        f'<div style="{style}" role="note" aria-label="{echapper_html(titre)}: {safe_contenu}">'
        f'<div style="font-weight: 600; color: {text_color}; margin-bottom: {Espacement.SM};">'
        f"{safe_titre}</div>"
        f'<div style="color: {text_color};">{safe_contenu}</div>'
        f"</div>"
    )


@composant_ui(
    "atoms",
    exemple='boite_info("Astuce", "Ctrl+S pour sauvegarder", "💡")',
    tags=["info", "callout"],
)
def boite_info(
    titre: str,
    contenu: str,
    icone: str = "ℹ️",
    variante: Variante = Variante.INFO,
):
    """
    Boîte d'information avec variante sémantique.

    Args:
        titre: Titre de la boîte
        contenu: Contenu textuel
        icone: Icône emoji
        variante: Variante visuelle (INFO, SUCCESS, WARNING, DANGER)

    Example:
        boite_info("Astuce", "Utilisez Ctrl+S pour sauvegarder", "💡")
        boite_info("Attention", "Stock faible", "⚠️", variante=Variante.WARNING)
    """
    bg, text_color, border_color = _obtenir_sem_variante(variante)

    container_cls = StyleSheet.create_class(
        {
            "background": bg,
            "border-left": f"4px solid {border_color}",
            "padding": Espacement.MD,
            "border-radius": Rayon.SM,
            "margin": f"{Espacement.MD} 0",
        }
    )

    safe_titre = echapper_html(f"{icone} {titre}")
    safe_contenu = echapper_html(contenu)

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}" role="note" aria-label="{echapper_html(titre)}: {safe_contenu}">'
        f'<div style="font-weight: 600; color: {text_color}; margin-bottom: {Espacement.SM};">'
        f"{safe_titre}</div>"
        f'<div style="color: {text_color};">{safe_contenu}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


@composant_ui("atoms", exemple="boule_loto_html(7)", tags=("loto", "html", "pure"))
def boule_loto_html(numero: int, is_chance: bool = False, taille: int = 50) -> str:
    """Génère le HTML d'une boule de loto (fonction pure, testable).

    Args:
        numero: Numéro à afficher
        is_chance: True pour style numéro chance (rose)
        taille: Taille en pixels

    Returns:
        Chaîne HTML de la boule.
    """
    gradient = (
        f"linear-gradient(135deg, {Couleur.LOTO_CHANCE_START} 0%, {Couleur.LOTO_CHANCE_END} 100%)"
        if is_chance
        else f"linear-gradient(135deg, {Couleur.LOTO_NORMAL_START} 0%, {Couleur.LOTO_NORMAL_END} 100%)"
    )
    font_size = int(taille * 0.4)

    style = (
        f"background: {gradient}; color: white; border-radius: 50%; "
        f"width: {taille}px; height: {taille}px; display: flex; "
        f"align-items: center; justify-content: center; margin: auto;"
    )

    return (
        f'<div style="{style}" role="img" aria-label="Boule numéro {numero}">'
        f'<span style="font-size: {font_size}px; font-weight: bold;">{numero}</span>'
        f"</div>"
    )


@composant_ui(
    "atoms",
    exemple="boule_loto(7)",
    tags=["loto", "ball", "jeux"],
)
def boule_loto(numero: int, is_chance: bool = False, taille: int = 50) -> None:
    """
    Boule de loto stylisée avec dégradé.

    Args:
        numero: Numéro à afficher (1-49 ou numéro chance)
        is_chance: True pour style numéro chance (rose), False pour normal (bleu)
        taille: Taille en pixels (défaut: 50)

    Example:
        boule_loto(7)  # Boule bleue normale
        boule_loto(3, is_chance=True)  # Boule chance rose
        boule_loto(42, taille=60)  # Plus grande
    """
    gradient = (
        f"linear-gradient(135deg, {Couleur.LOTO_CHANCE_START} 0%, {Couleur.LOTO_CHANCE_END} 100%)"
        if is_chance
        else f"linear-gradient(135deg, {Couleur.LOTO_NORMAL_START} 0%, {Couleur.LOTO_NORMAL_END} 100%)"
    )
    font_size = int(taille * 0.4)

    circle_cls = StyleSheet.create_class(
        {
            "background": gradient,
            "color": "white",
            "border-radius": "50%",
            "width": f"{taille}px",
            "height": f"{taille}px",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "margin": "auto",
        }
    )

    StyleSheet.inject()
    st.markdown(
        f'<div class="{circle_cls}" role="img" aria-label="Boule numéro {numero}">'
        f'<span style="font-size: {font_size}px; font-weight: bold;">{numero}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )
