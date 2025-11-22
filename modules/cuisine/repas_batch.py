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
    # Sélection recette
    # -------------------------
    recipes = pd.read_sql("SELECT id, name FROM recipes", conn)
    if recipes.empty:
        st.warning("Aucune recette disponible. Veuillez en ajouter dans le module Recettes.")
        return

    recipe_dict = dict(zip(recipes['name'], recipes['id']))

    selected_recipe = st.selectbox("Choisir une recette", recipes['name'])
    scheduled_date = st.date_input("Date prévue", value=datetime.today())

    # -------------------------
    # Ajouter Batch Meal
    # -------------------------
    if st.button("➕ Ajouter le batch meal"):
        recipe_id = recipe_dict[selected_recipe]

        cursor.execute(
            "INSERT INTO batch_meals (recipe_id, scheduled_date) VALUES (?, ?)",
            (recipe_id, scheduled_date.isoformat())
        )
        conn.commit()
        batch_id = cursor.lastrowid

        # Récupérer les ingrédients liés à la recette
        cursor.execute("""
                       SELECT i.id AS ingredient_id, i.name AS name, ri.quantity AS qty, i.unit
                       FROM recipe_ingredients ri
                                JOIN ingredients i ON i.id = ri.ingredient_id
                       WHERE ri.recipe_id = ?
                       """, (recipe_id,))
        ingredients = cursor.fetchall()

        missing = []

        # Vérifier inventaire et créer batch_meal_items
        for ing in ingredients:
            ingredient_id = ing["ingredient_id"]
            ing_name = ing["name"]
            needed_qty = ing["qty"]

            cursor.execute("SELECT quantity FROM inventory_items WHERE name = ?", (ing_name,))
            inv = cursor.fetchone()

            if not inv or inv["quantity"] < needed_qty:
                missing.append(ing_name)

            cursor.execute("""
                           INSERT INTO batch_meal_items (batch_meal_id, ingredient_id, quantity)
                           VALUES (?, ?, ?)
                           """, (batch_id, ingredient_id, needed_qty))

        conn.commit()

        if missing:
            st.warning("⚠️ Ingrédients insuffisants :")
            for m in missing:
                st.write(f"• {m}")

            cursor.execute("""
                           INSERT INTO user_notifications (user_id, module, message, created_at, read)
                           VALUES (1, ?, ?, datetime('now'), 0)
                           """, ("Repas Batch", f"Ingrédients manquants pour '{selected_recipe}'"))
            conn.commit()
        else:
            st.success(f"Batch meal '{selected_recipe}' ajouté ✅")

    # -------------------------
    # Affichage des batch meals
    # -------------------------
    df_batches = pd.read_sql("""
                             SELECT bm.id, bm.scheduled_date, r.name AS recipe_name
                             FROM batch_meals bm
                                      LEFT JOIN recipes r ON bm.recipe_id = r.id
                             ORDER BY bm.scheduled_date DESC
                             """, conn)

    if df_batches.empty:
        st.info("Aucun batch meal planifié.")
    else:
        st.subheader("📋 Liste des repas batch planifiés")
        st.dataframe(df_batches)

        for _, row in df_batches.iterrows():
            st.markdown(f"### {row['recipe_name']} – {row['scheduled_date']}")

            cursor.execute("""
                           SELECT i.name, bmi.quantity, i.unit
                           FROM batch_meal_items bmi
                                    JOIN ingredients i ON i.id = bmi.ingredient_id
                           WHERE bmi.batch_meal_id = ?
                           """, (row["id"],))

            items = cursor.fetchall()
            if items:
                st.table(pd.DataFrame(items, columns=["Nom", "Quantité", "Unité"]))

    conn.close()