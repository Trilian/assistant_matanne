"""
Cartes métriques avancées pour le tableau de bord.

Implémentées avec Box/Text primitives et StyleSheet pour la déduplication CSS.

Fournit des composants pour afficher:
- Métriques avec delta
- KPIs colorés
- Widgets famille (Jules, météo)
"""

import logging
from datetime import date
from typing import Any

import streamlit as st

from src.ui.primitives.box import Box
from src.ui.primitives.text import Text
from src.ui.registry import composant_ui
from src.ui.system.css import StyleSheet
from src.ui.tokens import Couleur, Espacement, Rayon, Typographie, gradient_subtil
from src.ui.utils import echapper_html

logger = logging.getLogger(__name__)


@composant_ui(
    "metrics",
    exemple='carte_metrique_avancee("Recettes", 42, "🍽️")',
    tags=["metric", "kpi", "dashboard"],
)
def carte_metrique_avancee(
    titre: str,
    valeur: Any,
    icone: str,
    delta: str | None = None,
    delta_positif: bool = True,
    sous_titre: str | None = None,
    couleur: str = Couleur.ACCENT,
    lien_module: str | None = None,
):
    """
    Carte métrique stylisée.

    Utilise ``StyleSheet`` pour le conteneur (déduplication) et ``Text``
    pour l'échappement automatique du contenu.

    Args:
        titre: Titre de la métrique
        valeur: Valeur principale
        icone: Emoji icône
        delta: Variation (optionnel)
        delta_positif: Si la variation est positive
        sous_titre: Texte secondaire
        couleur: Couleur d'accent
        lien_module: Module vers lequel naviguer
    """
    # Conteneur avec border-left (hors BoxProps)
    container_cls = StyleSheet.create_class(
        {
            "background": gradient_subtil(couleur),
            "border-left": f"4px solid {couleur}",
            "border-radius": Rayon.LG,
            "padding": "1.2rem",
            "margin-bottom": Espacement.SM,
        }
    )

    # Delta optionnel
    delta_html = ""
    if delta:
        delta_color = Couleur.DELTA_POSITIVE if delta_positif else Couleur.DELTA_NEGATIVE
        delta_arrow = "↑" if delta_positif else "↓"
        delta_html = (
            f'<span style="color: {delta_color}; font-size: 0.9rem;">'
            f"{delta_arrow} {echapper_html(delta)}</span>"
        )

    # Sous-titre optionnel
    sous_titre_html = (
        Text(
            sous_titre,
            size="xs",
            color=Couleur.TEXT_SECONDARY,
            tag="p",
        ).html()
        if sous_titre
        else ""
    )

    # Contenu structuré
    inner = Box(display="flex", justify="between", align="start")
    inner.child(
        f"<div>"
        f'<p style="color: {Couleur.TEXT_SECONDARY}; margin: 0 0 0.3rem 0; font-size: 0.9rem;">'
        f"{echapper_html(titre)}</p>"
        f'<h2 style="margin: 0; color: {Couleur.TEXT_PRIMARY};">'
        f"{echapper_html(str(valeur))}</h2>"
        f"{delta_html}"
        f"{sous_titre_html}"
        f"</div>"
    )
    inner.child(f'<span style="font-size: {Typographie.ICON_LG};">{echapper_html(icone)}</span>')

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}">{inner.html()}</div>',
        unsafe_allow_html=True,
    )

    if lien_module:
        if st.button(f"Voir {titre}", key=f"link_{lien_module}", use_container_width=True):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers(lien_module)
            st.rerun()


@composant_ui("metrics", exemple="widget_jules_apercu()", tags=["jules", "famille", "dashboard"])
def widget_jules_apercu(date_naissance: date | None = None):
    """Widget d'aperçu de Jules pour le dashboard.

    Utilise ``Box`` pour le conteneur gradient centré.

    Args:
        date_naissance: Date de naissance de Jules. Si None, utilise la
            valeur par défaut (15/06/2024).
    """
    from src.core.constants import JULES_NAISSANCE

    naissance = date_naissance or JULES_NAISSANCE
    aujourd_hui = date.today()
    age_jours = (aujourd_hui - naissance).days
    age_mois = age_jours // 30

    container = Box(
        bg=f"linear-gradient(135deg, {Couleur.BG_JULES_START}, {Couleur.BG_JULES_END})",
        radius=Rayon.XL,
        p=Espacement.LG,
        text_align="center",
    )
    container.child(f'<span style="font-size: {Typographie.ICON_XL};">👶</span>')
    container.child(Text("Jules", size="2xl", weight="bold", mt=Espacement.SM, tag="h3").html())
    container.child(
        Text(
            f"{age_mois} mois",
            weight="medium",
            color=Couleur.JULES_PRIMARY,
            tag="p",
        ).html()
    )
    container.show()


@composant_ui(
    "metrics",
    exemple='widget_meteo_jour({"temp": 22, "condition": "☀️ Ensoleillé", "conseil": "Promenade"})',
    tags=["meteo", "weather", "dashboard"],
)
def widget_meteo_jour(donnees_meteo: dict | None = None):
    """Widget météo simplifié.

    Utilise ``Box`` pour le conteneur gradient centré et ``Text``
    pour l'échappement automatique.

    Args:
        donnees_meteo: Dict avec les clés 'temp', 'condition', 'conseil'.
            Si None, affiche un placeholder.
    """
    if donnees_meteo is None:
        st.info("🌤️ Données météo non disponibles")
        return

    meteo = donnees_meteo
    condition_parts = meteo.get("condition", "").split()
    icone_meteo = condition_parts[0] if condition_parts else "🌤️"

    safe_temp = echapper_html(str(meteo.get("temp", "")))

    container = Box(
        bg=f"linear-gradient(135deg, {Couleur.BG_METEO_START}, {Couleur.BG_METEO_END})",
        radius=Rayon.LG,
        p=Espacement.MD,
        text_align="center",
    )
    container.child(f'<span style="font-size: {Typographie.ICON_MD};">{icone_meteo}</span>')
    container.child(
        f'<p style="margin: 0.3rem 0; font-size: {Typographie.H3}; font-weight: 600;">'
        f"{safe_temp}°C</p>"
    )
    container.child(
        Text(
            str(meteo.get("conseil", "")),
            size="xs",
            color=Couleur.TEXT_SECONDARY,
            tag="small",
        ).html()
    )
    container.show()
