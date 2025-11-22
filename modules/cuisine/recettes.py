# assistant_matanne/modules/recettes.py

import streamlit as st
import pandas as pd
from core.database import get_connection
from core.helpers import log_function
from core.services.gpt_recipe_service import generate_recipe_gpt, parse_recipe_json, insert_recipe_in_db


@log_function
def app():
    st.header("🍲 Recettes")

    conn = get_connection()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()

    st.markdown("Gérez vos recettes : ajout, modification, import GPT, suppression, export…")

    # =====================================================
    # 🔎 SECTION 1 : RECHERCHE & LISTE DES RECETTES
    # =====================================================
    st.subheader("📘 Liste des recettes")

    search = st.text_input("Rechercher une recette")
    if search:
        cursor.execute("SELECT * FROM recipes WHERE name LIKE ?", (f"%{search}%",))
    else:
        cursor.execute("SELECT * FROM recipes ORDER BY name ASC")
    recipes = cursor.fetchall()

    df = pd.DataFrame(recipes)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucune recette trouvée.")

    st.markdown("---")

    # =====================================================
    # ➕ SECTION 2 : AJOUT MANUEL
    # =====================================================

    st.subheader("➕ Ajouter une recette manuellement")

    with st.expander("Ajouter une nouvelle recette"):
        name = st.text_input("Nom de la recette *")
        category = st.text_input("Catégorie")
        instructions = st.text_area("Instructions")

        ing_names = st.text_area("Ingrédients (un par ligne : nom, quantité, unité)\nEx :\nCarottes, 200, g\nOeufs, 2, unités")

        if st.button("Ajouter", key="add_manual_recipe"):
            if not name.strip():
                st.error("Le nom est obligatoire.")
            else:
                cursor.execute("INSERT INTO recipes (name, category, instructions) VALUES (?, ?, ?)",
                               (name.strip(), category.strip(), instructions.strip()))
                recipe_id = cursor.lastrowid

                # Ajout des ingrédients
                if ing_names.strip():
                    for line in ing_names.split("\n"):
                        try:
                            ing_name, qty, unit = [x.strip() for x in line.split(",")]
                            qty = float(qty)
                        except:
                            st.warning(f"Ligne ignorée : {line}")
                            continue

                        # Vérifier si ingrédient existe
                        cursor.execute("SELECT id FROM ingredients WHERE LOWER(name)=LOWER(?)", (ing_name,))
                        row = cursor.fetchone()
                        if row:
                            ing_id = row["id"]
                        else:
                            cursor.execute("INSERT INTO ingredients (name, unit) VALUES (?, ?)", (ing_name, unit))
                            ing_id = cursor.lastrowid

                        cursor.execute("""
                                       INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
                                       VALUES (?, ?, ?)
                                       """, (recipe_id, ing_id, qty))

                conn.commit()
                st.success("Recette ajoutée !")

    st.markdown("---")

    # =====================================================
    # 🤖 SECTION 3 : GPT — AJOUT AUTOMATIQUE
    # =====================================================

    st.subheader("🤖 Ajouter une recette depuis GPT")

    with st.expander("Générer une recette avec GPT"):
        gpt_prompt = st.text_area("Décris ta recette :", placeholder="Je veux une recette de lasagnes simples, 4 personnes…")

        if st.button("Générer avec GPT"):
            if not gpt_prompt.strip():
                st.error("Merci d’entrer une description.")
            else:
                with st.spinner("Génération de la recette…"):
                    raw_json = generate_recipe_gpt(gpt_prompt, st.secrets["API_KEY"])

                try:
                    recipe_data = parse_recipe_json(raw_json)
                except Exception as e:
                    st.error(f"Erreur JSON : {e}")
                    st.code(raw_json)
                    return

                # Insertion en DB
                try:
                    insert_recipe_in_db(recipe_data)
                    st.success(f"Recette '{recipe_data['name']}' ajoutée à la base !")
                    st.json(recipe_data)
                except Exception as e:
                    st.error(f"Erreur lors de l'insertion : {e}")

    st.markdown("---")

    # =====================================================
    # ✏️ SECTION 4 : ÉDITION / SUPPRESSION
    # =====================================================

    st.subheader("✏️ Éditer ou supprimer une recette")

    recipe_list = [r["name"] for r in recipes] if recipes else []
    selected = st.selectbox("Choisir une recette", [""] + recipe_list)

    if selected:
        cursor.execute("SELECT * FROM recipes WHERE name=?", (selected,))
        r = cursor.fetchone()

        new_name = st.text_input("Nom", r["name"])
        new_category = st.text_input("Catégorie", r["category"])
        new_instructions = st.text_area("Instructions", r["instructions"])

        if st.button("💾 Sauvegarder modifications"):
            cursor.execute("""
                           UPDATE recipes
                           SET name=?, category=?, instructions=?
                           WHERE id=?
                           """, (new_name, new_category, new_instructions, r["id"]))
            conn.commit()
            st.success("Modifications enregistrées.")

        if st.button("🗑️ Supprimer cette recette"):
            cursor.execute("DELETE FROM recipes WHERE id=?", (r["id"],))
            cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?", (r["id"],))
            conn.commit()
            st.error("Recette supprimée.")

    st.markdown("---")

    # =====================================================
    # 📤 SECTION 5 : EXPORT CSV
    # =====================================================

    st.subheader("📤 Export des recettes")

    if st.button("Exporter en CSV"):
        df = pd.read_sql("SELECT * FROM recipes", conn)
        st.download_button(
            "Télécharger recettes.csv",
            df.to_csv(index=False),
            "recettes.csv",
            "text/csv"
        )

    conn.close()