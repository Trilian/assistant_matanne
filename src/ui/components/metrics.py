"""
Cartes métriques avancées pour le tableau de bord.

Fournit des composants pour afficher:
- Métriques avec delta
- KPIs colorés
- Widgets famille (Jules, météo)
"""

import logging
from datetime import date
from typing import Any

import streamlit as st

from src.ui.registry import composant_ui
from src.ui.tokens import Couleur, Espacement, Rayon, Typographie, gradient_subtil
from src.ui.utils import echapper_html

logger = logging.getLogger(__name__)


@st.cache_data(ttl=60)
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
    delta_html = ""
    if delta:
        delta_color = Couleur.DELTA_POSITIVE if delta_positif else Couleur.DELTA_NEGATIVE
        delta_arrow = "↑" if delta_positif else "↓"
        delta_html = f'<span style="color: {delta_color}; font-size: 0.9rem;">{delta_arrow} {echapper_html(delta)}</span>'

    sous_titre_html = (
        f'<p style="color: {Couleur.TEXT_SECONDARY}; margin: 0; font-size: {Typographie.CAPTION};">{echapper_html(sous_titre)}</p>'
        if sous_titre
        else ""
    )

    html = f"""
    <div style="
        background: {gradient_subtil(couleur)};
        border-left: 4px solid {couleur};
        border-radius: {Rayon.LG};
        padding: 1.2rem;
        margin-bottom: {Espacement.SM};
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <p style="color: {Couleur.TEXT_SECONDARY}; margin: 0 0 0.3rem 0; font-size: 0.9rem;">{echapper_html(titre)}</p>
                <h2 style="margin: 0; color: {Couleur.TEXT_PRIMARY};">{echapper_html(str(valeur))}</h2>
                {delta_html}
                {sous_titre_html}
            </div>
            <span style="font-size: {Typographie.ICON_LG};">{echapper_html(icone)}</span>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

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

    # Calculer l'âge de Jules
    from src.core.constants import JULES_NAISSANCE

    naissance = date_naissance or JULES_NAISSANCE
    aujourd_hui = date.today()
    age_jours = (aujourd_hui - naissance).days
    age_mois = age_jours // 30

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {Couleur.BG_JULES_START}, {Couleur.BG_JULES_END});
            border-radius: {Rayon.XL};
            padding: {Espacement.LG};
            text-align: center;
        ">
            <span style="font-size: {Typographie.ICON_XL};">👶</span>
            <h3 style="margin: {Espacement.SM} 0;">Jules</h3>
            <p style="margin: 0; color: {Couleur.JULES_PRIMARY}; font-weight: 500;">{age_mois} mois</p>
        </div>
        """,
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

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {Couleur.BG_METEO_START}, {Couleur.BG_METEO_END});
            border-radius: {Rayon.LG};
            padding: {Espacement.MD};
            text-align: center;
        ">
            <span style="font-size: {Typographie.ICON_MD};">{meteo["condition"].split()[0]}</span>
            <p style="margin: 0.3rem 0; font-size: {Typographie.H3}; font-weight: 600;">{meteo["temp"]}°C</p>
            <small style="color: {Couleur.TEXT_SECONDARY};">{meteo["conseil"]}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
