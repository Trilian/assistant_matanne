import streamlit as st
from core.database import get_connection
from core.helpers import log_function
import pandas as pd
import altair as alt
import io

def app():
    st.header("Recettes – Phase 4")
    st.subheader("Gestion des recettes avec import/export et alertes")

    conn = get_connection()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()

    if 'refresh' not in st.session_state:
        st.session_state['refresh'] = False

    # --- Affichage tableau et graphique ---
    def afficher_recettes():
        cursor.execute("SELECT * FROM recipes")
        recettes = cursor.fetchall()
        if recettes:
            df_recettes = pd.DataFrame(recettes)

            # Vérifier disponibilité des ingrédients
            cursor.execute("""
                           SELECT i.name AS ingredient, ri.recipe_id
                           FROM ingredients i
                                    JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
                           """)
            inventaire = cursor.execute("SELECT name FROM inventory_items").fetchall()
            inventaire = [r['name'] for r in inventaire]

            alert_badges = []
            for r in recettes:
                ing_ids = [ri['ingredient'] for ri in cursor.execute(
                    "SELECT i.name AS ingredient FROM ingredients i "
                    "JOIN recipe_ingredients ri ON i.id = ri.ingredient_id "
                    "WHERE ri.recipe_id=?", (r['id'],)
                ).fetchall()]
                if all(i in inventaire for i in ing_ids):
                    alert_badges.append("")
                else:
                    alert_badges.append("⚠️ ingrédients manquants")
            df_recettes['alerte'] = alert_badges
            st.dataframe(df_recettes[['name','alerte']], width=700)

            # Graphique nombre d'ingrédients
            ing_counts = []
            for r in recettes:
                count = cursor.execute(
                    "SELECT COUNT(*) as c FROM recipe_ingredients WHERE recipe_id=?", (r['id'],)
                ).fetchone()['c']
                ing_counts.append({'name': r['name'], 'ingredients': count})
            df_ing = pd.DataFrame(ing_counts)
            chart = alt.Chart(df_ing).mark_bar().encode(
                x='name',
                y='ingredients',
                color=alt.condition(
                    alt.datum.ingredients <= 2,
                    alt.value("orange"),
                    alt.value("green")
                ),
                tooltip=['name','ingredients']
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Aucune recette pour le moment.")

    # --- Ajouter recette ---
    with st.expander("Ajouter une recette"):
        nom_recette = st.text_input("Nom de la recette")
        ingredient_input = st.text_area("Ingrédients (nom:quantité par ligne, ex: Carotte:2)")

        @log_function
        def ajouter_recette(nom_recette, ingredient_input):
            cursor.execute("INSERT INTO recipes (name) VALUES (?)", (nom_recette,))
            recette_id = cursor.lastrowid
            for line in ingredient_input.splitlines():
                if ":" in line:
                    nom_ing, qty = line.split(":")
                    # Vérifier si l'ingrédient existe déjà
                    cursor.execute("SELECT id FROM ingredients WHERE name=?", (nom_ing.strip(),))
                    res = cursor.fetchone()
                    if res:
                        ing_id = res['id']
                    else:
                        cursor.execute("INSERT INTO ingredients (name, unit) VALUES (?, ?)", (nom_ing.strip(), ''))
                        ing_id = cursor.lastrowid
                    cursor.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                                   (recette_id, ing_id, float(qty.strip())))
            conn.commit()
            st.success(f"Recette '{nom_recette}' ajoutée !")
            st.session_state['refresh'] = not st.session_state['refresh']

        if st.button("Ajouter recette"):
            if nom_recette.strip() == "":
                st.error("Le nom de la recette ne peut pas être vide.")
            else:
                ajouter_recette(nom_recette, ingredient_input)

    # --- Import CSV ---
    with st.expander("Importer depuis CSV"):
        file = st.file_uploader("Sélectionner fichier CSV", type=["csv"])
        if file is not None:
            df_import = pd.read_csv(file)
            for _, row in df_import.iterrows():
                cursor.execute("INSERT INTO recipes (name) VALUES (?)", (row['name'],))
                recette_id = cursor.lastrowid
                if 'ingredients' in row and isinstance(row['ingredients'], str):
                    for ing in row['ingredients'].split(","):
                        if ":" in ing:
                            nom_ing, qty = ing.split(":")
                            cursor.execute("SELECT id FROM ingredients WHERE name=?", (nom_ing.strip(),))
                            res = cursor.fetchone()
                            if res:
                                ing_id = res['id']
                            else:
                                cursor.execute("INSERT INTO ingredients (name, unit) VALUES (?, ?)", (nom_ing.strip(), ''))
                                ing_id = cursor.lastrowid
                            cursor.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                                           (recette_id, ing_id, float(qty.strip())))
            conn.commit()
            st.success("Import terminé !")
            st.session_state['refresh'] = not st.session_state['refresh']

    # --- Export CSV ---
    with st.expander("Exporter en CSV"):
        cursor.execute("SELECT * FROM recipes")
        recettes = cursor.fetchall()
        if recettes:
            df_export = pd.DataFrame(recettes)
            ing_list = []
            for r in recettes:
                cursor.execute("""
                               SELECT i.name, ri.quantity FROM ingredients i
                                                                   JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
                               WHERE ri.recipe_id=?
                               """, (r['id'],))
                ingredients = [f"{i['name']}:{i['quantity']}" for i in cursor.fetchall()]
                ing_list.append(",".join(ingredients))
            df_export['ingredients'] = ing_list

            csv_buffer = io.StringIO()
            df_export.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Télécharger les recettes CSV",
                data=csv_buffer.getvalue(),
                file_name="recettes.csv",
                mime="text/csv"
            )
        else:
            st.info("Aucune recette à exporter.")

    # --- Affichage final ---
    afficher_recettes()
