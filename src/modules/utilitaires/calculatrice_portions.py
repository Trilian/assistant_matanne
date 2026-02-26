"""
Module Calculatrice de Portions — Ajustement intelligent des quantités.

Permet de recalculer les ingrédients d'une recette pour un nombre
de personnes différent, avec arrondis intelligents (pas de "2.33 œufs").
"""

import logging
import math

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("calc_portions")

# Ingrédients à arrondir à l'unité (on ne coupe pas un œuf en 3)
INGREDIENTS_UNITAIRES = {
    "oeuf",
    "oeufs",
    "œuf",
    "œufs",
    "egg",
    "eggs",
    "tomate",
    "tomates",
    "pomme",
    "pommes",
    "oignon",
    "oignons",
    "gousse",
    "gousses",
    "feuille",
    "feuilles",
    "tranche",
    "tranches",
    "sachet",
    "sachets",
    "bâtonnet",
    "bâtonnets",
}

# Palliers d'arrondi pour les mesures courantes
ARRONDIS_INTELLIGENTS = {
    "g": [5, 10, 25, 50],
    "kg": [0.1, 0.25, 0.5],
    "ml": [5, 10, 25, 50],
    "cl": [1, 5, 10],
    "L": [0.1, 0.25, 0.5],
    "cuillère": [0.25, 0.5, 1],
}


def arrondi_intelligent(valeur: float, unite: str, ingredient: str) -> str:
    """Arrondi intelligent selon le type d'ingrédient et l'unité."""
    # Ingrédients unitaires → arrondi à l'entier supérieur
    ingredient_lower = ingredient.lower().strip()
    for mot in INGREDIENTS_UNITAIRES:
        if mot in ingredient_lower:
            return str(math.ceil(valeur))

    # Arrondi standard selon l'unité
    unite_lower = unite.lower().strip()
    for key, paliers in ARRONDIS_INTELLIGENTS.items():
        if key in unite_lower:
            meilleur = valeur
            meilleure_diff = float("inf")
            for p in paliers:
                arrondi = round(valeur / p) * p
                if arrondi > 0 and abs(arrondi - valeur) < meilleure_diff:
                    meilleure_diff = abs(arrondi - valeur)
                    meilleur = arrondi
            if meilleur == int(meilleur):
                return str(int(meilleur))
            return f"{meilleur:.1f}"

    # Par défaut, 1 décimale
    if valeur == int(valeur):
        return str(int(valeur))
    return f"{valeur:.1f}"


@profiler_rerun("calculatrice_portions")
def app():
    """Point d'entrée module Calculatrice de Portions."""
    st.title("🔢 Calculatrice de Portions")
    st.caption("Ajustez les quantités d'une recette en un clic")

    with error_boundary(titre="Erreur calculatrice"):
        tab1, tab2 = st.tabs(["🧮 Calculatrice", "📋 Recette rapide"])

        with tab1:
            _calculatrice_simple()
        with tab2:
            _recette_rapide()


def _calculatrice_simple():
    """Calculatrice de conversion simple."""
    st.subheader("🧮 Conversion rapide")

    col1, col2, col3 = st.columns(3)
    with col1:
        portions_originales = st.number_input(
            "Portions d'origine",
            min_value=1,
            value=4,
            step=1,
            key=_keys("orig"),
        )
    with col2:
        portions_voulues = st.number_input(
            "Portions voulues",
            min_value=1,
            value=6,
            step=1,
            key=_keys("voulu"),
        )
    with col3:
        ratio = portions_voulues / portions_originales
        st.metric("Facteur", f"×{ratio:.2f}")

    st.divider()

    # Tableau d'ingrédients dynamique
    st.markdown("**Ingrédients:**")

    nb_ingredients = st.number_input(
        "Nombre d'ingrédients",
        min_value=1,
        max_value=30,
        value=5,
        key=_keys("nb_ing"),
    )

    resultats = []
    for i in range(nb_ingredients):
        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 2])
        with col1:
            nom = st.text_input(
                "Ingrédient",
                key=_keys("ing_nom", str(i)),
                label_visibility="collapsed",
                placeholder=f"Ingrédient {i + 1}",
            )
        with col2:
            quantite = st.number_input(
                "Qté",
                min_value=0.0,
                step=0.5,
                key=_keys("ing_qty", str(i)),
                label_visibility="collapsed",
            )
        with col3:
            unite = st.text_input(
                "Unité",
                key=_keys("ing_unite", str(i)),
                label_visibility="collapsed",
                placeholder="g, ml, pcs...",
            )
        with col4:
            if nom and quantite > 0:
                nouvelle_qty = quantite * ratio
                arrondi = arrondi_intelligent(nouvelle_qty, unite, nom)
                st.markdown(f"→ **{arrondi} {unite}**")
                resultats.append((nom, arrondi, unite))
            else:
                st.markdown("—")


def _recette_rapide():
    """Convertir une recette collée en texte libre."""
    st.subheader("📋 Coller une recette")
    st.caption("Collez la liste d'ingrédients, un par ligne (format: quantité unité ingrédient)")

    col1, col2 = st.columns(2)
    with col1:
        portions_orig = st.number_input(
            "Portions d'origine", min_value=1, value=4, key=_keys("rr_orig")
        )
    with col2:
        portions_new = st.number_input(
            "Portions voulues", min_value=1, value=6, key=_keys("rr_new")
        )

    texte = st.text_area(
        "Ingrédients (un par ligne)",
        height=200,
        placeholder="200 g farine\n3 oeufs\n100 ml lait\n1 sachet levure",
        key=_keys("rr_texte"),
    )

    if texte and st.button("🔄 Convertir", key=_keys("rr_convert"), use_container_width=True):
        ratio = portions_new / portions_orig
        lignes = texte.strip().split("\n")

        st.markdown(f"**Recette pour {portions_new} personnes** (×{ratio:.2f}):")
        st.divider()

        for ligne in lignes:
            ligne = ligne.strip()
            if not ligne:
                continue

            # Parser: essayer de détecter nombre + unité + ingrédient
            parts = ligne.split(None, 2)
            try:
                quantite = float(parts[0].replace(",", "."))
                if len(parts) >= 3:
                    unite = parts[1]
                    ingredient = parts[2]
                elif len(parts) == 2:
                    unite = ""
                    ingredient = parts[1]
                else:
                    unite = ""
                    ingredient = ""

                nouvelle_qty = quantite * ratio
                arrondi = arrondi_intelligent(nouvelle_qty, unite, ingredient)
                st.markdown(f"- **{arrondi}** {unite} {ingredient}")
            except (ValueError, IndexError):
                # Ligne non parsable → afficher telle quelle
                st.markdown(f"- {ligne}")
