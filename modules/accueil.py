# assistant_matanne/modules/accueil.py

import streamlit as st
import pandas as pd
from datetime import date
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("Accueil")
    st.subheader("Bienvenue dans Assistant MaTanne")

    create_all_tables()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Statistiques globales
        cursor.execute("SELECT COUNT(*) FROM recipes")
        recipes_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM inventory_items")
        inventory_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM batch_meals")
        batch_count = cursor.fetchone()[0]

        st.write(f"Nombre de recettes : {recipes_count}")
        st.write(f"Nombre d'items en inventaire : {inventory_count}")
        st.write(f"Nombre de repas batch : {batch_count}")

        # Profil Jules
        cursor.execute("SELECT name, birth_date FROM child_profiles LIMIT 1")
        row = cursor.fetchone()
        if row:
            name, birth_date = row
            birth_date = date.fromisoformat(birth_date)
            age_months = (date.today().year - birth_date.year) * 12 + (date.today().month - birth_date.month)
            st.write(f"Profil de l'enfant : {name}, {age_months} mois")
        else:
            st.info("Aucun profil enfant trouvé")

        # Export recettes et inventaire
        if st.button("Exporter recettes"):
            df = pd.read_sql("SELECT * FROM recipes", conn)
            st.download_button("Télécharger CSV", df.to_csv(index=False), "recettes.csv", "text/csv")

        if st.button("Exporter inventaire"):
            df = pd.read_sql("SELECT * FROM inventory_items", conn)
            st.download_button("Télécharger CSV", df.to_csv(index=False), "inventaire.csv", "text/csv")

        # Ajout rapide à l’inventaire
        with st.expander("Ajouter un item à l'inventaire"):
            name = st.text_input("Nom")
            category = st.text_input("Catégorie")
            quantity = st.number_input("Quantité", min_value=0.0)
            unit = st.text_input("Unité")
            if st.button("Ajouter"):
                if name:
                    cursor.execute(
                        "INSERT INTO inventory_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)",
                        (name, category, quantity, unit)
                    )
                    conn.commit()
                    st.success(f"Item '{name}' ajouté à l'inventaire")
                else:
                    st.error("Le nom de l'item est requis")
    finally:
        conn.close()