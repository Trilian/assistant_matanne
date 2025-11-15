# assistant_matanne/modules/accueil.py

import streamlit as st
import pandas as pd
from datetime import date
from core.database import get_connection
from core.helpers import log_function


@log_function
def app():
    st.header("Accueil")
    st.subheader("Bienvenue dans Assistant MaTanne")

    # Connexion DB
    conn = get_connection()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()

    if "refresh" not in st.session_state:
        st.session_state["refresh"] = False

    try:
        # --- Statistiques globales ---
        def safe_count(query: str, label: str):
            """Exécute un COUNT(*) sécurisé avec clé 'c'."""
            try:
                cursor.execute(f"{query} as c")
                return cursor.fetchone()["c"]
            except Exception as e:
                st.warning(f"Erreur lors de la récupération de {label} : {e}")
                return 0

        recipes_count = safe_count("SELECT COUNT(*) FROM recipes", "recettes")
        inventory_count = safe_count("SELECT COUNT(*) FROM inventory_items", "inventaire")
        batch_count = safe_count("SELECT COUNT(*) FROM batch_meals", "batch meals")

        st.write(f"📘 Nombre de recettes : **{recipes_count}**")
        st.write(f"📦 Nombre d'items en inventaire : **{inventory_count}**")
        st.write(f"🍱 Nombre de repas batch : **{batch_count}**")

        st.markdown("---")

        # --- Profil enfant ---
        cursor.execute("SELECT name, birth_date FROM child_profiles LIMIT 1")
        row = cursor.fetchone()

        st.subheader("👶 Profil enfant")
        if row:
            name = row.get("name")
            birth_raw = row.get("birth_date")

            try:
                birth_date = date.fromisoformat(birth_raw)
                age_months = (date.today().year - birth_date.year) * 12 + (date.today().month - birth_date.month)

                st.info(f"**{name}**, {age_months} mois")
            except Exception:
                st.error(f"Date de naissance invalide dans la base : '{birth_raw}'")
        else:
            st.info("Aucun profil enfant trouvé.")

        st.markdown("---")

        # --- Boutons d'export ---
        st.subheader("📤 Export de données")

        if st.button("Exporter recettes"):
            df = pd.read_sql("SELECT * FROM recipes", conn)
            st.download_button(
                "Télécharger CSV recettes",
                df.to_csv(index=False),
                "recettes.csv",
                "text/csv"
            )

        if st.button("Exporter inventaire"):
            df = pd.read_sql("SELECT * FROM inventory_items", conn)
            st.download_button(
                "Télécharger CSV inventaire",
                df.to_csv(index=False),
                "inventaire.csv",
                "text/csv"
            )

        st.markdown("---")

        # --- Ajout rapide à l’inventaire ---
        st.subheader("➕ Ajouter un item à l'inventaire")
        with st.expander("Ajouter un item"):

            name = st.text_input("Nom *")
            category = st.text_input("Catégorie")
            quantity = st.number_input("Quantité", min_value=0.0, format="%.2f")
            unit = st.text_input("Unité")

            if st.button("Ajouter", key="add_inventory"):
                if not name.strip():
                    st.error("Le nom de l'item est requis.")
                else:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO inventory_items (name, category, quantity, unit)
                            VALUES (?, ?, ?, ?)
                            """,
                            (name.strip(), category.strip(), quantity, unit.strip())
                        )
                        conn.commit()
                        st.success(f"Item '{name}' ajouté à l'inventaire !")
                        st.session_state["refresh"] = not st.session_state["refresh"]
                    except Exception as e:
                        st.error(f"Erreur lors de l'ajout : {e}")

    finally:
        conn.close()