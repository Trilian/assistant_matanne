"""
Module Convertisseur d'Unités Cuisine — Outil de conversion rapide.

Conversions poids, volumes, températures avec prise en compte
de la densité des ingrédients pour les conversions cups/grammes.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("convertisseur")

# Densités courantes (g par cup de 240ml)
DENSITES_INGREDIENTS = {
    "Farine (blé T55)": 120,
    "Farine complète": 130,
    "Sucre en poudre": 200,
    "Sucre glace": 120,
    "Cassonade": 220,
    "Beurre": 230,
    "Huile": 220,
    "Lait": 245,
    "Eau": 240,
    "Crème fraîche": 240,
    "Riz": 185,
    "Flocons d'avoine": 90,
    "Poudre d'amande": 100,
    "Cacao en poudre": 85,
    "Fécule de maïs": 130,
    "Miel": 340,
    "Sel fin": 290,
    "Levure chimique": 190,
    "Parmesan râpé": 100,
    "Noix de coco râpée": 95,
    "Pépites de chocolat": 170,
    "Chapelure": 110,
}

# Volumes (en ml)
VOLUMES = {
    "ml": 1,
    "cl": 10,
    "dl": 100,
    "L": 1000,
    "cuillère à café": 5,
    "cuillère à soupe": 15,
    "cup (US)": 240,
    "fl oz": 29.574,
    "pint (US)": 473,
}

# Poids (en grammes)
POIDS = {
    "g": 1,
    "kg": 1000,
    "mg": 0.001,
    "oz": 28.3495,
    "lb (livre)": 453.592,
}

# Températures
TEMPERATURES = {
    "Celsius": "°C",
    "Fahrenheit": "°F",
    "Thermostat": "Th.",
}


@profiler_rerun("convertisseur_unites")
def app():
    """Point d'entrée module Convertisseur d'Unités."""
    st.title("⚖️ Convertisseur d'Unités Cuisine")
    st.caption("Conversions rapides pour la cuisine")

    with error_boundary(titre="Erreur convertisseur"):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["⚖️ Poids", "🥛 Volumes", "🌡️ Températures", "🥣 Cups ↔ Grammes"]
        )

        with tab1:
            _convertir_poids()
        with tab2:
            _convertir_volumes()
        with tab3:
            _convertir_temperatures()
        with tab4:
            _convertir_cups_grammes()


def _convertir_poids():
    """Conversion entre unités de poids."""
    st.subheader("⚖️ Conversion de Poids")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        valeur = st.number_input(
            "Valeur", min_value=0.0, value=100.0, step=1.0, key=_keys("poids_val")
        )
    with col2:
        de = st.selectbox("De", options=list(POIDS.keys()), key=_keys("poids_de"))
    with col3:
        vers = st.selectbox(
            "Vers",
            options=list(POIDS.keys()),
            index=1,
            key=_keys("poids_vers"),
        )

    if de and vers:
        en_grammes = valeur * POIDS[de]
        resultat = en_grammes / POIDS[vers]
        st.success(f"**{valeur} {de}** = **{resultat:.2f} {vers}**")


def _convertir_volumes():
    """Conversion entre unités de volume."""
    st.subheader("🥛 Conversion de Volumes")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        valeur = st.number_input(
            "Valeur", min_value=0.0, value=250.0, step=1.0, key=_keys("vol_val")
        )
    with col2:
        de = st.selectbox("De", options=list(VOLUMES.keys()), key=_keys("vol_de"))
    with col3:
        vers = st.selectbox(
            "Vers",
            options=list(VOLUMES.keys()),
            index=1,
            key=_keys("vol_vers"),
        )

    if de and vers:
        en_ml = valeur * VOLUMES[de]
        resultat = en_ml / VOLUMES[vers]
        st.success(f"**{valeur} {de}** = **{resultat:.2f} {vers}**")

    # Aide-mémoire
    with st.expander("📖 Aide-mémoire volumes"):
        st.markdown("""
        | Mesure | Équivalent |
        |--------|-----------|
        | 1 cuillère à café | 5 ml |
        | 1 cuillère à soupe | 15 ml |
        | 1 cup (US) | 240 ml |
        | 1 verre | ~200 ml |
        | 1 bol | ~350 ml |
        """)


def _convertir_temperatures():
    """Conversion de températures (Celsius, Fahrenheit, Thermostat)."""
    st.subheader("🌡️ Conversion de Températures")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        valeur = st.number_input(
            "Valeur", min_value=-273.0, value=180.0, step=5.0, key=_keys("temp_val")
        )
    with col2:
        de = st.selectbox("De", options=list(TEMPERATURES.keys()), key=_keys("temp_de"))
    with col3:
        vers = st.selectbox(
            "Vers",
            options=list(TEMPERATURES.keys()),
            index=1,
            key=_keys("temp_vers"),
        )

    # Conversion via Celsius comme pivot
    if de == "Celsius":
        celsius = valeur
    elif de == "Fahrenheit":
        celsius = (valeur - 32) * 5 / 9
    else:  # Thermostat
        celsius = valeur * 30

    if vers == "Celsius":
        resultat = celsius
    elif vers == "Fahrenheit":
        resultat = celsius * 9 / 5 + 32
    else:  # Thermostat
        resultat = celsius / 30

    symbole_de = TEMPERATURES[de]
    symbole_vers = TEMPERATURES[vers]
    st.success(f"**{valeur} {symbole_de}** = **{resultat:.1f} {symbole_vers}**")

    # Repères four
    with st.expander("🔥 Repères de cuisson au four"):
        st.markdown("""
        | Thermostat | °C | °F | Usage |
        |-----------|-----|-----|-------|
        | Th. 3 | 90°C | 195°F | Séchage, meringues |
        | Th. 4 | 120°C | 250°F | Cuisson lente |
        | Th. 5 | 150°C | 300°F | Pâtisseries délicates |
        | Th. 6 | 180°C | 355°F | Gâteaux, gratins |
        | Th. 7 | 210°C | 410°F | Tartes, quiches |
        | Th. 8 | 240°C | 465°F | Pizzas, pains |
        | Th. 9 | 270°C | 520°F | Grillades vives |
        """)


def _convertir_cups_grammes():
    """Conversion cups ↔ grammes avec densité des ingrédients."""
    st.subheader("🥣 Cups ↔ Grammes")
    st.caption("Conversion précise selon la densité de l'ingrédient")

    ingredient = st.selectbox(
        "Ingrédient",
        options=list(DENSITES_INGREDIENTS.keys()),
        key=_keys("cup_ingredient"),
    )

    densite = DENSITES_INGREDIENTS[ingredient]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Cups → Grammes**")
        cups = st.number_input(
            "Nombre de cups",
            min_value=0.0,
            value=1.0,
            step=0.25,
            key=_keys("cups_to_g"),
        )
        grammes = cups * densite
        st.success(f"**{cups} cup(s)** de {ingredient} = **{grammes:.0f} g**")

    with col2:
        st.markdown("**Grammes → Cups**")
        g = st.number_input(
            "Grammes",
            min_value=0.0,
            value=float(densite),
            step=10.0,
            key=_keys("g_to_cups"),
        )
        cups_result = g / densite
        # Fraction lisible
        fractions = {0.25: "¼", 0.33: "⅓", 0.5: "½", 0.67: "⅔", 0.75: "¾"}
        frac_part = cups_result - int(cups_result)
        frac_str = ""
        for threshold, symbol in fractions.items():
            if abs(frac_part - threshold) < 0.05:
                frac_str = (
                    f" (≈ {int(cups_result)} {symbol} cup)"
                    if int(cups_result)
                    else f" (≈ {symbol} cup)"
                )
                break
        st.success(f"**{g:.0f} g** de {ingredient} = **{cups_result:.2f} cup(s)**{frac_str}")

    # Tableau récapitulatif
    with st.expander("📊 Table complète des densités"):
        data = [
            {"Ingrédient": k, "g/cup": v, "1/2 cup (g)": v // 2, "1/4 cup (g)": v // 4}
            for k, v in DENSITES_INGREDIENTS.items()
        ]
        st.dataframe(data, use_container_width=True)
