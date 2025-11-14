# assistant_matanne/modules/repas_batch.py

import streamlit as st
import pandas as pd
from datetime import datetime
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

@log_function
def app():
    st.header("🥘 Repas Batch")
    st.subheader("Planification et suivi des repas")

    create_all_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # Sélection d'une recette pour batch meal
    # -------------------------
    recipes = pd.read_sql("SELECT id, name FROM recipes", conn)
    if recipes.empty:
        st.warning("Aucune recette disponible. Veuillez en ajouter dans le module Recettes.")
        return

    recipe_dict = dict(zip(recipes['name'], recipes['id']))
    selected_recipe = st.selectbox("Choisir une recette", recipes['name'])
    scheduled_date = st.date_input("Date prévue", value=datetime.today())

    if st.button("➕ Ajouter le batch meal"):
        recipe_id = recipe_dict[selected_recipe]
        # Ajouter le batch meal
        cursor.execute(
            "INSERT INTO batch_meals (recipe_id, scheduled_date) VALUES (?, ?)",
            (recipe_id, scheduled_date.isoformat())
        )
        conn.commit()
        batch_id = cursor.lastrowid

        # Récupérer les ingrédients de la recette
        cursor.execute(
            """SELECT ingredient_id, quantity FROM recipe_ingredients WHERE recipe_id = ?""",
            (recipe_id,)
        )
        ingredients = cursor.fetchall()

        # Ajouter batch_meal_items et vérifier inventaire
        missing_ingredients = []
        for ing_id, qty in ingredients:
            cursor.execute(
                "SELECT quantity FROM inventory_items WHERE id = ?",
                (ing_id,)
            )
            inv_qty = cursor.fetchone()
            if not inv_qty or inv_qty[0] < qty:
                missing_ingredients.append(ing_id)

            cursor.execute(
                "INSERT INTO batch_meal_items (batch_meal_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                (batch_id, ing_id, qty)
            )

        conn.commit()

        if missing_ingredients:
            st.warning("⚠️ Certains ingrédients sont insuffisants dans l’inventaire.")
            for mid in missing_ingredients:
                cursor.execute("SELECT name FROM ingredients WHERE id = ?", (mid,))
                ing_name = cursor.fetchone()[0]
                st.write(f"- {ing_name}")
            # Ajouter une notification
            cursor.execute(
                "INSERT INTO user_notifications (user_id, module, message, created_at, read) VALUES (1, ?, ?, datetime('now'), 0)",
                ("Repas Batch", f"Batch meal '{selected_recipe}' planifié avec ingrédients manquants."),
            )
            conn.commit()
        else:
            st.success(f"Batch meal '{selected_recipe}' ajouté ✅")

    # -------------------------
    # Affichage des batch meals
    # -------------------------
    df_batches = pd.read_sql(
        """SELECT bm.id, bm.scheduled_date, r.name as recipe_name
           FROM batch_meals bm
                    LEFT JOIN recipes r ON bm.recipe_id = r.id
           ORDER BY bm.scheduled_date DESC""",
        conn
    )

    if df_batches.empty:
        st.info("Aucun batch meal planifié.")
    else:
        st.subheader("📋 Liste des repas batch planifiés")
        st.dataframe(df_batches)

        # Afficher les ingrédients par batch
        for _, row in df_batches.iterrows():
            st.markdown(f"**{row['recipe_name']}** – {row['scheduled_date']}")
            cursor.execute(
                """SELECT i.name, bmi.quantity, i.unit
                   FROM batch_meal_items bmi
                            LEFT JOIN ingredients i ON bmi.ingredient_id = i.id
                   WHERE bmi.batch_meal_id = ?""",
                (row['id'],)
            )
            items = cursor.fetchall()
            if items:
                df_items = pd.DataFrame(items, columns=["Nom", "Quantité", "Unité"])
                st.table(df_items)

    # -------------------------
    # Export CSV
    # -------------------------
    st.markdown("---")
    if st.button("📦 Exporter les batch meals"):
        df_batches.to_csv("batch_meals_export.csv", index=False)
        st.download_button(
            "Télécharger CSV", "batch_meals_export.csv", "batch_meals_export.csv", "text/csv"
        )

    conn.close()