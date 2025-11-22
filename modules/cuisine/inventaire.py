# assistant_matanne/modules/inventaire.py

import streamlit as st
import pandas as pd
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables

def normalize_name(s):
    if s is None:
        return ""
    return str(s).strip().lower()

@log_function
def app():
    st.header("📦 Inventaire — Version PRO")
    st.subheader("Gestion complète du stock, recherche, édition, alertes et liste de courses")

    create_all_tables()
    conn = get_connection()
    conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    cursor = conn.cursor()

    st.markdown("---")

    # --------------------------
    # Recherche + filtres
    # --------------------------
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        search = st.text_input("Recherche (nom, catégorie)", "")
    with col_r2:
        show_low = st.checkbox("Afficher le stock faible uniquement (< 3)", False)

    # --------------------------
    # Lecture inventaire
    # --------------------------
    df = pd.read_sql("SELECT * FROM inventory_items ORDER BY name COLLATE NOCASE", conn)

    # Filtrer
    if search.strip():
        token = search.strip().lower()
        df = df[
            df["name"].str.lower().str.contains(token)
            | df["category"].fillna("").str.lower().str.contains(token)
            ]

    if show_low:
        df = df[df["quantity"] < 3]

    if df.empty:
        st.info("Aucun item dans l'inventaire.")
    else:
        # Alert low stock
        low_stock = df[df["quantity"] < 3]
        if not low_stock.empty:
            st.warning("⚠️ Stock faible pour certains items :")
            st.dataframe(low_stock[["name", "quantity", "unit"]])

        st.dataframe(df)

    st.markdown("---")

    # --------------------------
    # Ajouter un item
    # --------------------------
    with st.expander("➕ Ajouter un item"):
        name = st.text_input("Nom")
        category = st.text_input("Catégorie")
        quantity = st.number_input("Quantité", min_value=0.0)
        unit = st.text_input("Unité")

        if st.button("Ajouter dans inventaire"):
            if not name.strip():
                st.error("Le nom est obligatoire.")
            else:
                cursor.execute("""
                               INSERT INTO inventory_items (name, category, quantity, unit)
                               VALUES (?, ?, ?, ?)
                               """, (name.strip(), category.strip(), quantity, unit.strip()))
                conn.commit()
                st.success(f"'{name}' ajouté.")
                st.experimental_rerun()

    # --------------------------
    # Éditer un item existant
    # --------------------------
    if not df.empty:
        st.markdown("### ✏️ Modifier un item")

        selected = st.selectbox(
            "Choisir un produit",
            df["name"].tolist(),
            key="edit_select"
        )

        row = df[df["name"] == selected].iloc[0]

        with st.form("edit_form"):
            e_name = st.text_input("Nom", row["name"])
            e_cat = st.text_input("Catégorie", row["category"])
            e_qty = st.number_input("Quantité", value=float(row["quantity"]), min_value=0.0)
            e_unit = st.text_input("Unité", row["unit"])
            save = st.form_submit_button("Enregistrer les modifications")

            if save:
                cursor.execute("""
                               UPDATE inventory_items
                               SET name=?, category=?, quantity=?, unit=?
                               WHERE id=?
                               """, (e_name.strip(), e_cat.strip(), e_qty, e_unit.strip(), row["id"]))
                conn.commit()
                st.success("Item mis à jour.")
                st.experimental_rerun()

    # --------------------------
    # Supprimer un item
    # --------------------------
    if not df.empty:
        st.markdown("### 🗑️ Supprimer un item")

        delete_item = st.selectbox("Item à supprimer", df["name"].tolist(), key="del_select")

        if st.button("Supprimer"):
            cursor.execute("DELETE FROM inventory_items WHERE name = ?", (delete_item,))
            conn.commit()
            st.success(f"'{delete_item}' supprimé.")
            st.experimental_rerun()

    # --------------------------
    # Liste de courses
    # --------------------------
    st.markdown("---")
    st.subheader("🛒 Liste de courses")

    df_courses = pd.read_sql(
        """SELECT c.id, i.name, c.needed_quantity
           FROM courses c
                    LEFT JOIN inventory_items i ON c.item_id = i.id""",
        conn
    )

    if df_courses.empty:
        st.info("La liste de courses est vide.")
    else:
        st.dataframe(df_courses)

        # Supprimer un item de la liste de course
        del_course = st.selectbox("Supprimer de la liste :", df_courses["name"].tolist(), key="del_course")
        if st.button("Retirer de la liste"):
            cursor.execute("""
                           DELETE FROM courses
                           WHERE id = (SELECT id FROM courses WHERE item_id =
                                                                    (SELECT id FROM inventory_items WHERE name=?))
                           """, (del_course,))
            conn.commit()
            st.success(f"'{del_course}' retiré.")
            st.experimental_rerun()

    # Export
    if st.button("Exporter inventaire en CSV"):
        st.download_button("Télécharger CSV", df.to_csv(index=False), "inventaire.csv", "text/csv")

    conn.close()