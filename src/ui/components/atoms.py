"""
UI Components - Atoms (composants de base)
badge, etat_vide, carte_metrique, separateur, boite_info, boule_loto

Implémentés avec les primitives Box/Text et le système CVA
pour la déduplication CSS et l'échappement automatique.

Note: Pour des métriques plus avancées avec icônes et liens,
utilisez carte_metrique_avancee depuis src.ui.components.metrics
"""

from __future__ import annotations

import streamlit as st

from src.ui.primitives.box import Box
from src.ui.primitives.text import Text
from src.ui.registry import composant_ui
from src.ui.system.css import StyleSheet
from src.ui.system.variants import BADGE_VARIANTS, cva
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

# ── Générateur CVA pré-compilé ─────────────────────────────
_badge_style = cva(BADGE_VARIANTS)


@composant_ui("atoms", exemple='badge("Actif", variante=Variante.SUCCESS)', tags=["badge", "label"])
def badge(
    texte: str,
    variante: Variante | None = None,
    couleur: str | None = None,
) -> None:
    """
    Badge coloré avec variante sémantique.

    Utilise ``cva(BADGE_VARIANTS)`` pour la résolution des styles.

    Args:
        texte: Texte du badge
        variante: Variante sémantique (SUCCESS, WARNING, DANGER, INFO, NEUTRAL, ACCENT)
        couleur: Couleur brute (hex) — déprécié, préférer ``variante``

    Example:
        badge("Actif", variante=Variante.SUCCESS)
        badge("Urgent", variante=Variante.DANGER)
    """
    safe_text = echapper_html(texte)

    if couleur and variante is None:
        # Rétrocompatibilité : couleur brute → inline style (pas de preset CVA)
        st.markdown(
            f'<span style="display: inline-flex; background: {couleur}; color: white; '
            f"padding: {Espacement.XS} 0.75rem; border-radius: {Rayon.PILL}; "
            f'font-size: {Typographie.BODY_SM}; font-weight: 600;">{safe_text}</span>',
            unsafe_allow_html=True,
        )
    else:
        # CVA : résolution automatique des styles depuis BADGE_VARIANTS
        variant_name = variante.value if variante else "success"
        style = _badge_style(variant=variant_name)
        st.markdown(
            f'<span style="{style}">{safe_text}</span>',
            unsafe_allow_html=True,
        )


@composant_ui("atoms", exemple='etat_vide("Aucune recette", "🍽️")', tags=["empty", "placeholder"])
def etat_vide(message: str, icone: str = "📭", sous_texte: str | None = None):
    """
    État vide centré.

    Utilise ``Box`` (flexbox column centré) + ``Text`` (échappement auto).

    Args:
        message: Message principal
        icone: Icône (emoji)
        sous_texte: Texte secondaire

    Example:
        etat_vide("Aucune recette", "🍽️", "Ajoutez-en une")
    """
    container = Box(
        display="flex",
        direction="column",
        align="center",
        p=Espacement.XXL,
        color=Couleur.TEXT_SECONDARY,
        text_align="center",
    )

    # Icône (taille DISPLAY hors du mapping Text)
    container.child(
        f'<div style="font-size: {Typographie.DISPLAY};">' f"{echapper_html(icone)}</div>"
    )

    # Message principal
    container.child(Text(message, size="2xl", weight="medium", mt=Espacement.MD, tag="div").html())

    # Sous-texte optionnel
    if sous_texte:
        container.child(Text(sous_texte, size="md", mt=Espacement.SM, tag="div").html())

    container.show()


@composant_ui("atoms", exemple='carte_metrique("Total", "42", "+5")', tags=["metric", "kpi"])
def carte_metrique(
    label: str,
    valeur: str,
    delta: str | None = None,
    couleur: str = Couleur.BG_SURFACE,
):
    """
    Carte métrique simple.

    Utilise ``Box`` pour la carte et ``Text`` pour le contenu échappé.

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
    card = Box(bg=couleur, p=Espacement.LG, radius=Rayon.LG, shadow=Ombre.SM)

    # Label
    card.child(
        Text(
            label,
            size="sm",
            weight="medium",
            color=Couleur.TEXT_SECONDARY,
            tag="div",
        ).html()
    )

    # Valeur
    card.child(Text(valeur, size="3xl", weight="bold", mt=Espacement.SM, tag="div").html())

    # Delta optionnel
    if delta:
        delta_str = str(delta).strip()
        if delta_str.startswith("-") or delta_str.startswith("↓"):
            delta_couleur = Couleur.DELTA_NEGATIVE
        elif delta_str in ("0", "+0"):
            delta_couleur = Couleur.TEXT_SECONDARY
        else:
            delta_couleur = Couleur.DELTA_POSITIVE
        card.child(
            Text(
                delta,
                size="sm",
                color=delta_couleur,
                mt=Espacement.XS,
                tag="div",
            ).html()
        )

    card.show()


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
            f"background: var(--sem-surface, {Couleur.BG_SURFACE}); "
            f'position: relative; top: -0.75rem;">{echapper_html(texte)}</span>'
            f'<hr style="margin-top: -{Espacement.LG}; '
            f'border: 1px solid {Couleur.BORDER_LIGHT};">'
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

    Utilise ``StyleSheet`` pour la classe du conteneur (déduplication)
    et ``Text`` pour l'échappement automatique du contenu.

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

    # Classe CSS dédupliquée via StyleSheet (border-left hors BoxProps)
    container_cls = StyleSheet.create_class(
        {
            "background": bg,
            "border-left": f"4px solid {border_color}",
            "padding": Espacement.MD,
            "border-radius": Rayon.SM,
            "margin": f"{Espacement.MD} 0",
        }
    )

    header = Text(
        f"{icone} {titre}",
        weight="semibold",
        color=text_color,
        mb=Espacement.SM,
        tag="div",
    )
    body = Text(contenu, color=text_color, tag="div")

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}">{header.html()}{body.html()}</div>',
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

    Utilise ``Box`` pour le conteneur circulaire.

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
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        if is_chance
        else "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    )
    font_size = int(taille * 0.4)

    circle = Box(
        bg=gradient,
        color="white",
        radius="50%",
        w=f"{taille}px",
        h=f"{taille}px",
        display="flex",
        align="center",
        justify="center",
        m="auto",
    )
    circle.child(f'<span style="font-size: {font_size}px; font-weight: bold;">{numero}</span>')
    circle.show()
