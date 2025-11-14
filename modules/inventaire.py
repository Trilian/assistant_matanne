# assistant_matanne/modules/inventaire.py

import streamlit as st
import pandas as pd
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("Inventaire")
    st.subheader("Gestion des produits et alertes de stock")

    create_all_tables()
    conn = get_connection()
    try:
        # Affichage inventaire
        df_inventory = pd.read_sql("SELECT id, name, category, quantity, unit FROM inventory_items", conn)
        if df_inventory.empty:
            st.info("Inventaire vide")
        else:
            # Alerting : stock faible
            threshold = 3  # seuil à adapter
            low_stock = df_inventory[df_inventory['quantity'] <= threshold]
            if not low_stock.empty:
                st.warning("⚠️ Certains items sont en stock faible ou presque épuisés :")
                st.dataframe(low_stock[['name','quantity','unit']])

            st.dataframe(df_inventory)

            # Export CSV
            if st.button("Exporter inventaire"):
                st.download_button("Télécharger CSV", df_inventory.to_csv(index=False), "inventaire.csv", "text/csv")

        # Ajouter un item
        with st.expander("Ajouter un item à l'inventaire"):
            name = st.text_input("Nom")
            category = st.text_input("Catégorie")
            quantity = st.number_input("Quantité", min_value=0.0)
            unit = st.text_input("Unité")
            if st.button("Ajouter"):
                if name:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO inventory_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)",
                        (name, category, quantity, unit)
                    )
                    conn.commit()
                    st.success(f"Item '{name}' ajouté")
                else:
                    st.error("Le nom de l'item est requis")

        # Liste de courses
        df_courses = pd.read_sql(
            "SELECT c.id, i.name, c.needed_quantity FROM courses c LEFT JOIN inventory_items i ON c.item_id = i.id", conn
        )
        if not df_courses.empty:
            st.subheader("Liste de courses")
            st.dataframe(df_courses)
            if st.button("Exporter liste de courses"):
                st.download_button("Télécharger CSV", df_courses.to_csv(index=False), "courses.csv", "text/csv")

    finally:
        conn.close()
