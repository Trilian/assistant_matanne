"""
Module Calculatrice Coût Repas — Estimation du prix d'un repas.

Croise les ingrédients d'une recette avec les prix moyens
pour calculer le coût par personne.
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("cout_repas")

# Prix moyens au kg/L en France (2024-2025)
PRIX_MOYENS = {
    "Farine": 1.20,
    "Sucre": 1.50,
    "Beurre": 10.00,
    "Lait": 1.10,
    "Œufs (x6)": 2.50,
    "Huile d'olive": 8.00,
    "Huile tournesol": 3.00,
    "Riz": 2.50,
    "Pâtes": 1.80,
    "Semoule": 2.00,
    "Pomme de terre": 1.50,
    "Carotte": 1.80,
    "Oignon": 2.00,
    "Tomate": 3.50,
    "Courgette": 3.00,
    "Poivron": 4.00,
    "Aubergine": 3.50,
    "Salade": 1.50,
    "Champignon": 5.00,
    "Poulet (entier)": 6.00,
    "Poulet (filet)": 11.00,
    "Bœuf haché": 12.00,
    "Bœuf (steak)": 18.00,
    "Porc (côte)": 8.00,
    "Saumon": 20.00,
    "Cabillaud": 15.00,
    "Thon (boîte)": 12.00,
    "Jambon": 15.00,
    "Lardons": 10.00,
    "Emmental": 10.00,
    "Mozzarella": 8.00,
    "Parmesan": 20.00,
    "Crème fraîche": 4.00,
    "Yaourt nature": 2.50,
    "Pain": 3.50,
    "Pomme": 3.00,
    "Banane": 2.00,
    "Orange": 2.50,
    "Sel": 0.50,
    "Poivre": 30.00,
    "Herbes (basilic, persil)": 15.00,
    "Ail": 8.00,
    "Chocolat noir": 10.00,
    "Miel": 15.00,
    "Levure": 10.00,
}


@profiler_rerun("cout_repas")
def app():
    """Point d'entrée module Coût Repas."""
    st.title("💰 Calculatrice Coût Repas")
    st.caption("Estimez le coût d'une recette par personne")

    with error_boundary(titre="Erreur coût repas"):
        tab1, tab2 = st.tabs(["🧮 Calculatrice", "📊 Prix de référence"])

        with tab1:
            _calculatrice()
        with tab2:
            _prix_reference()


def _calculatrice():
    """Interface de calcul du coût."""
    nb_personnes = st.number_input(
        "Nombre de personnes",
        min_value=1,
        max_value=20,
        value=4,
        key=_keys("nb_pers"),
    )

    st.subheader("📋 Ingrédients")

    nb_ingredients = st.number_input(
        "Nombre d'ingrédients",
        min_value=1,
        max_value=20,
        value=5,
        key=_keys("nb_ing"),
    )

    total = 0.0
    ingredients_details = []

    for i in range(nb_ingredients):
        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
        with col1:
            ingredient = st.selectbox(
                f"Ingrédient {i + 1}",
                options=["— Choisir —"] + list(PRIX_MOYENS.keys()),
                key=_keys("ing", str(i)),
                label_visibility="collapsed",
            )
        with col2:
            quantite = st.number_input(
                "Qté (g/ml)",
                min_value=0.0,
                step=10.0,
                key=_keys("qty", str(i)),
                label_visibility="collapsed",
            )
        with col3:
            if ingredient != "— Choisir —" and quantite > 0:
                prix_kg = PRIX_MOYENS.get(ingredient, 0)
                cout = (quantite / 1000) * prix_kg
                total += cout
                st.markdown(f"**{cout:.2f} €**")
                ingredients_details.append((ingredient, quantite, cout))
            else:
                st.markdown("—")
        with col4:
            if ingredient != "— Choisir —" and quantite > 0:
                prix_kg = PRIX_MOYENS.get(ingredient, 0)
                st.caption(f"{prix_kg:.2f}€/kg")

    st.divider()

    # Résultats
    if total > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🍽️ Coût total", f"{total:.2f} €")
        with col2:
            par_personne = total / nb_personnes
            st.metric("👤 Par personne", f"{par_personne:.2f} €")
        with col3:
            st.metric(
                "🆚 vs Restaurant",
                f"~{max(0, 15 - par_personne):.0f} € économisés",
                help="Comparé à ~15€ le repas moyen au restaurant",
            )

        # Détail
        with st.expander("📊 Détail des coûts"):
            for ingredient, qty, cout in ingredients_details:
                pct = (cout / total) * 100
                st.progress(pct / 100, text=f"{ingredient}: {cout:.2f}€ ({pct:.0f}%)")
    else:
        st.info("👆 Sélectionnez des ingrédients et entrez les quantités.")


def _prix_reference():
    """Tableau des prix de référence."""
    st.subheader("📊 Prix moyens de référence (€/kg ou €/L)")
    st.caption("Prix moyens France, ajustez selon votre supermarché")

    data = [
        {
            "Ingrédient": k,
            "Prix (€/kg ou €/L)": f"{v:.2f}",
            "Prix 100g": f"{v / 10:.2f}",
        }
        for k, v in sorted(PRIX_MOYENS.items(), key=lambda x: x[1])
    ]
    st.dataframe(data, use_container_width=True)
