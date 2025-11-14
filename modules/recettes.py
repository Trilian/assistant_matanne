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
    cursor = conn.cursor()
    conn.commit()

    if 'refresh' not in st.session_state:
        st.session_state['refresh'] = False

    # --- Affichage tableau et graphique ---
    def afficher_recettes():
        cursor.execute("SELECT * FROM recettes")
        recettes = cursor.fetchall()
        if recettes:
            df_recettes = pd.DataFrame([dict(r) for r in recettes])

            # Vérifier disponibilité des ingrédients
            cursor.execute("SELECT nom FROM inventaire")
            inventaire = [r['nom'] for r in cursor.fetchall()]
            alert_badges = []
            for r in recettes:
                cursor.execute("SELECT nom FROM ingredients WHERE recette_id=?", (r['id'],))
                ings = [i['nom'] for i in cursor.fetchall()]
                if all(i in inventaire for i in ings):
                    alert_badges.append("")
                else:
                    alert_badges.append("⚠️ ingrédients manquants")

            df_recettes['alerte'] = alert_badges
            st.dataframe(df_recettes[['nom','alerte']], width=700)

            # Graphique nombre d'ingrédients
            ing_counts = []
            for r in recettes:
                cursor.execute("SELECT COUNT(*) as count FROM ingredients WHERE recette_id=?", (r['id'],))
                ing_counts.append({'nom': r['nom'], 'ingredients': cursor.fetchone()['count']})
            df_ing = pd.DataFrame(ing_counts)
            chart = alt.Chart(df_ing).mark_bar().encode(
                x='nom',
                y='ingredients',
                color=alt.condition(
                    alt.datum.ingredients <= 2,
                    alt.value("orange"),
                    alt.value("green")
                ),
                tooltip=['nom','ingredients']
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
            cursor.execute("INSERT INTO recettes (nom) VALUES (?)", (nom_recette,))
            recette_id = cursor.lastrowid
            for line in ingredient_input.splitlines():
                if ":" in line:
                    nom_ing, qty = line.split(":")
                    cursor.execute("INSERT INTO ingredients (recette_id, nom, quantite) VALUES (?, ?, ?)",
                                   (recette_id, nom_ing.strip(), int(qty.strip())))
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
                cursor.execute("INSERT INTO recettes (nom) VALUES (?)", (row['nom'],))
                recette_id = cursor.lastrowid
                if 'ingredients' in row and isinstance(row['ingredients'], str):
                    for ing in row['ingredients'].split(","):
                        if ":" in ing:
                            nom_ing, qty = ing.split(":")
                            cursor.execute("INSERT INTO ingredients (recette_id, nom, quantite) VALUES (?, ?, ?)",
                                           (recette_id, nom_ing.strip(), int(qty.strip())))
            conn.commit()
            st.success("Import terminé !")
            st.session_state['refresh'] = not st.session_state['refresh']

    # --- Export CSV ---
    with st.expander("Exporter en CSV"):
        cursor.execute("SELECT * FROM recettes")
        recettes = cursor.fetchall()
        if recettes:
            df_export = pd.DataFrame([dict(r) for r in recettes])
            # Ajouter ingrédients concaténés
            ing_list = []
            for r in recettes:
                cursor.execute("SELECT nom, quantite FROM ingredients WHERE recette_id=?", (r['id'],))
                ingredients = [f"{i['nom']}:{i['quantite']}" for i in cursor.fetchall()]
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