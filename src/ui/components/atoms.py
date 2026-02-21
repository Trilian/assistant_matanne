"""
UI Components - Atoms (composants de base)
badge, etat_vide, carte_metrique, separateur, boite_info

Note: Pour des métriques plus avancées avec icônes et liens,
utilisez carte_metrique_avancee depuis src.ui.components.metrics
"""

from __future__ import annotations

import streamlit as st

from src.ui.registry import composant_ui
from src.ui.tokens import (
    Couleur,
    Espacement,
    Ombre,
    Rayon,
    Typographie,
    Variante,
    obtenir_couleurs_variante,
)
from src.ui.utils import echapper_html


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
    if couleur and variante is None:
        # Rétrocompatibilité : couleur brute
        bg = couleur
        text_color = "white"
    elif variante is not None:
        bg, text_color, _ = obtenir_couleurs_variante(variante)
    else:
        bg, text_color, _ = obtenir_couleurs_variante(Variante.SUCCESS)

    st.markdown(
        f'<span style="background: {bg}; color: {text_color}; '
        f"padding: {Espacement.XS} 0.75rem; border-radius: {Rayon.PILL}; "
        f'font-size: {Typographie.BODY_SM}; font-weight: 600;">{echapper_html(texte)}</span>',
        unsafe_allow_html=True,
    )


@composant_ui("atoms", exemple='etat_vide("Aucune recette", "🍽️")', tags=["empty", "placeholder"])
def etat_vide(message: str, icone: str = "📭", sous_texte: str | None = None):
    """
    État vide centré

    Args:
        message: Message principal
        icone: Icône (emoji)
        sous_texte: Texte secondaire

    Example:
        etat_vide("Aucune recette", "🍽️", "Ajoutez-en une")
    """
    html_sous_texte = (
        f'<div style="font-size: {Typographie.BODY}; margin-top: {Espacement.SM};">'
        f"{echapper_html(sous_texte)}</div>"
        if sous_texte
        else ""
    )

    st.markdown(
        f'<div style="text-align: center; padding: {Espacement.XXL}; color: {Couleur.TEXT_SECONDARY};">'
        f'<div style="font-size: {Typographie.DISPLAY};">{echapper_html(icone)}</div>'
        f'<div style="font-size: {Typographie.H3}; margin-top: {Espacement.MD}; font-weight: 500;">'
        f"{echapper_html(message)}</div>"
        f"{html_sous_texte}"
        f"</div>",
        unsafe_allow_html=True,
    )


@composant_ui("atoms", exemple='carte_metrique("Total", "42", "+5")', tags=["metric", "kpi"])
def carte_metrique(
    label: str, valeur: str, delta: str | None = None, couleur: str = Couleur.BG_SURFACE
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

    Example:
        carte_metrique("Total", "42", "+5", "#f0f0f0")

    See Also:
        carte_metrique_avancee: Version avancée avec plus d'options
    """
    html_delta = (
        f'<div style="font-size: {Typographie.BODY_SM}; color: {Couleur.DELTA_POSITIVE}; '
        f'margin-top: {Espacement.XS};">{echapper_html(delta)}</div>'
        if delta
        else ""
    )

    st.markdown(
        f'<div style="background: {couleur}; padding: {Espacement.LG}; '
        f'border-radius: {Rayon.LG}; box-shadow: {Ombre.SM};">'
        f'<div style="font-size: {Typographie.BODY_SM}; color: {Couleur.TEXT_SECONDARY}; '
        f'font-weight: 500;">{echapper_html(label)}</div>'
        f'<div style="font-size: {Typographie.H2}; font-weight: 700; '
        f'margin-top: {Espacement.SM};">{echapper_html(valeur)}</div>'
        f"{html_delta}"
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
            f'<span style="padding: 0 {Espacement.MD}; background: white; '
            f'position: relative; top: -0.75rem;">{echapper_html(texte)}</span>'
            f'<hr style="margin-top: -{Espacement.LG}; border: 1px solid {Couleur.BORDER_LIGHT};">'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("---")


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
    bg, text_color, border_color = obtenir_couleurs_variante(variante)
    st.markdown(
        f'<div style="background: {bg}; border-left: 4px solid {border_color}; '
        f'padding: {Espacement.MD}; border-radius: {Rayon.SM}; margin: {Espacement.MD} 0;">'
        f'<div style="font-weight: 600; margin-bottom: {Espacement.SM}; color: {text_color};">'
        f"{echapper_html(icone)} {echapper_html(titre)}</div>"
        f'<div style="color: {text_color};">{echapper_html(contenu)}</div>'
        f"</div>",
        unsafe_allow_html=True,
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
    # Dégradé bleu pour boules normales, rose pour numéro chance
    gradient = (
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        if is_chance
        else "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    )
    font_size = int(taille * 0.4)

    st.markdown(
        f'<div style="background: {gradient}; color: white; border-radius: 50%; '
        f"width: {taille}px; height: {taille}px; display: flex; align-items: center; "
        f"justify-content: center; font-size: {font_size}px; font-weight: bold; "
        f'margin: auto;">{numero}</div>',
        unsafe_allow_html=True,
    )
