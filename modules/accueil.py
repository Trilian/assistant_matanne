# assistant_matanne/modules/accueil.py

import streamlit as st
import pandas as pd
from datetime import date
from core.database import get_connection
from core.helpers import log_function


@log_function
def app():
    # --- STYLE MODERNE ---
    st.markdown("""
        <style>
            .card {
                padding: 20px;
                border-radius: 16px;
                background: #f6f8f7;
                border: 1px solid #e2e8e5;
                box-shadow: 0 2px 4px rgba(0,0,0,0.04);
                margin-bottom: 10px;
            }
            .stat {
                font-size: 1.8rem;
                font-weight: 700;
                color: #2d4d36;
                margin-bottom: -5px;
            }
            .label {
                font-size: 0.9rem;
                color: #5e7a6a;
            }
            .tile {
                padding: 18px;
                background: #ffffff;
                border-radius: 14px;
                border: 1px solid #dfe7e2;
                transition: 0.15s ease;
                text-align: center;
                cursor: pointer;
                font-size: 1.1rem;
            }
            .tile:hover {
                background: #eef5f1;
                transform: translateY(-2px);
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 👋 Bienvenue dans **Assistant MaTanne**")
    st.caption("Votre tableau de bord familial : organisation, repas, jardin et projets.")

    conn = get_connection()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()

    # === Stats globales ===
    def quick_count(query):
        try:
            cursor.execute(query)
            return cursor.fetchone()["c"]
        except:
            return 0

    recipes = quick_count("SELECT COUNT(*) as c FROM recipes")
    items = quick_count("SELECT COUNT(*) as c FROM inventory_items")
    batch = quick_count("SELECT COUNT(*) as c FROM batch_meals")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><div class='stat'>" + str(recipes) +
                    "</div><div class='label'>Recettes</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><div class='stat'>" + str(items) +
                    "</div><div class='label'>Articles inventaire</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><div class='stat'>" + str(batch) +
                    "</div><div class='label'>Batch meals</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # === Profil enfant Jules ===
    st.markdown("### 👶 Aujourd’hui pour Jules")

    cursor.execute("SELECT name, birth_date FROM child_profiles LIMIT 1")
    row = cursor.fetchone()

    if row:
        name = row["name"]
        bd = row["birth_date"]

        try:
            birth_date = date.fromisoformat(bd)
            months = (date.today().year - birth_date.year) * 12 + (date.today().month - birth_date.month)
        except:
            months = "?"

        st.markdown(f"""
        <div class='card'>
            <b>{name}</b> — {months} mois<br>
            ❤️ Suivi enfant disponible dans le menu.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucun profil enfant enregistré.")

    st.markdown("---")

    # === Actions rapides ===
    st.markdown("### ⚡ Actions rapides")
    colA, colB = st.columns(2)

    with colA:
        if st.button("➕ Ajouter un item à l’inventaire"):
            st.session_state["force_open_inventory"] = True
            st.success("Aller à Inventaire → Ajout")

    with colB:
        if st.button("🍲 Ajouter une recette"):
            st.session_state["force_open_recipes"] = True
            st.success("Aller à Recettes → Ajout")

    st.markdown("---")

    # === Accès rapides — Tuiles modernes ===
    st.markdown("### 🚀 Accès rapides")

    tiles = {
        "🍲 Recettes": "🍲 Recettes",
        "📦 Inventaire": "📦 Inventaire",
        "🥘 Batch Cooking": "🥘 Repas Batch",
        "🏡 Projets": "🏡 Projets Maison",
        "🌱 Jardin": "🌱 Jardin",
        "⏰ Routines": "⏰ Routines",
    }

    cols = st.columns(3)
    i = 0
    for label in tiles:
        col = cols[i % 3]
        with col:
            if st.button(label, key=f"tile_{label}", use_container_width=True):
                st.session_state["sidebar_module_radio"] = tiles[label]
                st.experimental_rerun()
        i += 1

    conn.close()