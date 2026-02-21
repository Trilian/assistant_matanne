"""
Cartes métriques avancées pour le tableau de bord.

Implémentées avec StyleSheet pour la déduplication CSS.

Fournit des composants pour afficher:
- Métriques avec delta
- KPIs colorés
- Widgets famille (Jules, météo)
"""

import logging
from datetime import date
from typing import Any

import streamlit as st

from src.ui.engine import StyleSheet
from src.ui.registry import composant_ui
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
    container_cls = StyleSheet.create_class(
        {
            "background": gradient_subtil(couleur),
            "border-left": f"4px solid {couleur}",
            "border-radius": Rayon.LG,
            "padding": "1.2rem",
            "margin-bottom": Espacement.SM,
        }
    )

    inner_cls = StyleSheet.create_class(
        {
            "display": "flex",
            "justify-content": "space-between",
            "align-items": "flex-start",
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
    sous_titre_html = ""
    if sous_titre:
        sous_titre_html = (
            f'<p style="font-size: {Typographie.CAPTION}; color: {Couleur.TEXT_SECONDARY}; '
            f'margin: 0.2rem 0 0 0;">{echapper_html(sous_titre)}</p>'
        )

    safe_titre = echapper_html(titre)
    safe_valeur = echapper_html(str(valeur))
    safe_icone = echapper_html(icone)

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}">'
        f'<div class="{inner_cls}">'
        f"<div>"
        f'<p style="color: {Couleur.TEXT_SECONDARY}; margin: 0 0 0.3rem 0; font-size: 0.9rem;">'
        f"{safe_titre}</p>"
        f'<h2 style="margin: 0; color: {Couleur.TEXT_PRIMARY};">{safe_valeur}</h2>'
        f"{delta_html}"
        f"{sous_titre_html}"
        f"</div>"
        f'<span style="font-size: {Typographie.ICON_LG};">{safe_icone}</span>'
        f"</div>"
        f"</div>",
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

    Args:
        date_naissance: Date de naissance de Jules. Si None, utilise la
            valeur par défaut (15/06/2024).
    """
    from src.core.constants import JULES_NAISSANCE

    naissance = date_naissance or JULES_NAISSANCE
    aujourd_hui = date.today()
    age_jours = (aujourd_hui - naissance).days
    age_mois = age_jours // 30

    container_cls = StyleSheet.create_class(
        {
            "background": f"linear-gradient(135deg, {Couleur.BG_JULES_START}, {Couleur.BG_JULES_END})",
            "border-radius": Rayon.XL,
            "padding": Espacement.LG,
            "text-align": "center",
        }
    )

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}">'
        f'<span style="font-size: {Typographie.ICON_XL};">👶</span>'
        f'<h3 style="font-size: {Typographie.H3}; font-weight: bold; '
        f'margin-top: {Espacement.SM};">Jules</h3>'
        f'<p style="font-weight: 500; color: {Couleur.JULES_PRIMARY};">'
        f"{age_mois} mois</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


@composant_ui(
    "metrics",
    exemple='widget_meteo_jour({"temp": 22, "condition": "☀️ Ensoleillé", "conseil": "Promenade"})',
    tags=["meteo", "weather", "dashboard"],
)
def widget_meteo_jour(donnees_meteo: dict | None = None):
    """Widget météo simplifié.

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
    safe_conseil = echapper_html(str(meteo.get("conseil", "")))

    container_cls = StyleSheet.create_class(
        {
            "background": f"linear-gradient(135deg, {Couleur.BG_METEO_START}, {Couleur.BG_METEO_END})",
            "border-radius": Rayon.LG,
            "padding": Espacement.MD,
            "text-align": "center",
        }
    )

    StyleSheet.inject()
    st.markdown(
        f'<div class="{container_cls}">'
        f'<span style="font-size: {Typographie.ICON_MD};">{icone_meteo}</span>'
        f'<p style="margin: 0.3rem 0; font-size: {Typographie.H3}; font-weight: 600;">'
        f"{safe_temp}°C</p>"
        f'<small style="font-size: {Typographie.CAPTION}; color: {Couleur.TEXT_SECONDARY};">'
        f"{safe_conseil}</small>"
        f"</div>",
        unsafe_allow_html=True,
    )
