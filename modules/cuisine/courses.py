# assistant_matanne/modules/courses.py
"""
Module Courses — Version PRO (Option C)

Fonctionnalités :
- Affichage, recherche, filtres
- Ajout manuel avec autocomplétion depuis inventory_items
- Génération automatique depuis Recettes (ingrédients manquants)
- Génération depuis Batch Meals (ingrédients d'un batch planifié)
- Fusion / aggregation d'items identiques
- Export CSV
- Conversion d'un item "liste de courses" en inventaire (achat) et déduction automatique
- Suppression / marquage comme acheté
- Compatible avec schema_manager (tables : courses, inventory_items, recipes, recipe_ingredients, batch_meals, batch_meal_items, ingredients)
"""

import streamlit as st
import pandas as pd
import io
from core.database import get_connection
from core.helpers import log_function
from core.schema_manager import create_all_tables
from datetime import datetime

# ---------------------
# Helpers
# ---------------------
def normalize_name(s):
    if s is None:
        return ""
    return str(s).strip().lower()

def read_inventory(cursor):
    """Return dict normalized_name -> row dict (id,name,quantity,unit)."""
    inv = {}
    try:
        rows = cursor.execute("SELECT id, name, quantity, unit FROM inventory_items").fetchall()
        for r in rows:
            if isinstance(r, dict):
                _id = r.get("id")
                name = r.get("name") or ""
                qty = float(r.get("quantity") or 0.0)
                unit = r.get("unit") or ""
            else:
                _id = r[0]
                name = r[1]
                # depending on schema ordering, try safe access
                try:
                    qty = float(r[3]) if r[3] is not None else 0.0
                except Exception:
                    qty = 0.0
                unit = r[4] if len(r) > 4 else ""
            inv[normalize_name(name)] = {"id": _id, "name": name, "quantity": qty, "unit": unit}
    except Exception:
        return {}
    return inv

def read_courses_as_df(conn):
    try:
        df = pd.read_sql("""
                         SELECT c.id, i.name as item_name, c.needed_quantity, i.unit, COALESCE(i.id, c.item_id) as inventory_id
                         FROM courses c
                                  LEFT JOIN inventory_items i ON c.item_id = i.id
                         ORDER BY item_name COLLATE NOCASE
                         """, conn)
        return df
    except Exception:
        return pd.DataFrame(columns=["id","item_name","needed_quantity","unit","inventory_id"])

def merge_similar_courses(conn):
    """
    Merge duplicate course entries by name (case-insensitive) summing needed_quantity.
    Keep one entry and delete duplicates.
    """
    cursor = conn.cursor()
    try:
        rows = cursor.execute("SELECT id, item_id, needed_quantity FROM courses").fetchall()
        # Build map by normalized name (using inventory name if available)
        name_map = {}
        for r in rows:
            cid = r['id'] if isinstance(r, dict) else r[0]
            item_id = r['item_id'] if isinstance(r, dict) else r[1]
            needed = float(r['needed_quantity'] if isinstance(r, dict) else (r[2] or 0.0))
            # resolve name if possible
            if item_id:
                inv = cursor.execute("SELECT name FROM inventory_items WHERE id = ?", (item_id,)).fetchone()
                name = inv['name'] if inv and isinstance(inv, dict) else (inv[0] if inv else None)
            else:
                name = None
            n = normalize_name(name or "")
            if not n:
                n = f"__id_{item_id}"
            if n in name_map:
                name_map[n]['sum'] += needed
                name_map[n]['ids'].append(cid)
            else:
                name_map[n] = {'sum': needed, 'ids': [cid], 'item_id': item_id, 'name': name}
        # Now merge: keep first id, update its needed_quantity, delete others
        for k, v in name_map.items():
            ids = v['ids']
            if len(ids) <= 1:
                continue
            keep = ids[0]
            to_del = ids[1:]
            cursor.execute("UPDATE courses SET needed_quantity = ? WHERE id = ?", (v['sum'], keep))
            cursor.executemany("DELETE FROM courses WHERE id = ?", [(d,) for d in to_del])
        conn.commit()
    except Exception:
        conn.rollback()

# ---------------------
# Main App
# ---------------------
@log_function
def app():
    st.header("🛒 Liste de courses — PRO")
    st.subheader("Gestion intelligente, génération depuis recettes et batch, achat / conversion en inventaire")

    # Ensure tables exist (non-blocking)
    try:
        create_all_tables()
    except Exception:
        pass

    conn = get_connection()
    # don't change row_factory globally: pandas.read_sql expects default cursor behavior
    cursor = conn.cursor()

    # Top actions
    col_a, col_b, col_c = st.columns([1,1,1])
    with col_a:
        if st.button("🔄 Rafraîchir"):
            st.experimental_rerun()
    with col_b:
        if st.button("🔁 Fusionner doublons"):
            merge_similar_courses(conn)
            st.success("Doublons fusionnés.")
            st.experimental_rerun()
    with col_c:
        if st.button("📤 Export CSV"):
            df_exp = read_courses_as_df(conn)
            if df_exp.empty:
                st.info("Aucune course à exporter.")
            else:
                buf = io.StringIO()
                df_exp.to_csv(buf, index=False)
                st.download_button("Télécharger CSV", buf.getvalue(), "courses_export.csv", "text/csv")

    st.markdown("---")

    # Search / filters
    col1, col2 = st.columns([2,1])
    with col1:
        q = st.text_input("Rechercher un item (nom)", "")
    with col2:
        only_missing_inventory = st.checkbox("Afficher seulement items non présents en inventaire", value=False)

    # Show current courses
    df_courses = read_courses_as_df(conn)
    if not df_courses.empty:
        display_df = df_courses.copy()
        if q.strip():
            token = q.strip().lower()
            display_df = display_df[display_df["item_name"].str.lower().str.contains(token)]
        if only_missing_inventory:
            display_df = display_df[display_df["inventory_id"].isna()]

        st.subheader("📝 Items dans la liste")
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("La liste de courses est vide.")

    st.markdown("---")

    # Add manual item
    st.subheader("➕ Ajouter un item manuellement")
    inv_map = read_inventory(cursor)
    inv_names = sorted([v['name'] for v in inv_map.values()])

    m_col1, m_col2, m_col3 = st.columns([2,1,1])
    with m_col1:
        manual_name = st.text_input("Nom de l'item (autocomplétion depuis inventaire possible)")
    with m_col2:
        manual_qty = st.number_input("Quantité nécessaire", min_value=0.0, value=1.0, step=0.5)
    with m_col3:
        manual_unit = st.text_input("Unité (optionnel)")

    # Suggest autocompletion: simple dropdown
    if manual_name and manual_name.strip().lower() in [n.lower() for n in inv_names]:
        matched = [v for v in inv_map.values() if v['name'].strip().lower() == manual_name.strip().lower()][0]
        suggested_unit = matched.get("unit") or ""
    else:
        suggested_unit = manual_unit or ""

    if st.button("Ajouter à la liste"):
        name = manual_name.strip()
        if not name:
            st.error("Nom requis.")
        else:
            # If inventory item exists, link; else create course with NULL item_id
            inv_entry = None
            norm = normalize_name(name)
            if norm in inv_map:
                inv_entry = inv_map[norm]
                item_id = inv_entry["id"]
                unit = inv_entry.get("unit") or suggested_unit
            else:
                item_id = None
                unit = suggested_unit
            try:
                cursor.execute("INSERT INTO courses (item_id, needed_quantity) VALUES (?, ?)", (item_id, manual_qty))
                conn.commit()
                st.success(f"'{name}' ajouté à la liste.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erreur ajout : {e}")

    st.markdown("---")

    # Generate from a recipe: add missing ingredients
    st.subheader("⚡ Générer depuis une recette (ajoute seulement les ingrédients manquants)")
    try:
        recipes = pd.read_sql("SELECT id, name FROM recipes ORDER BY name COLLATE NOCASE", conn)
    except Exception:
        recipes = pd.DataFrame(columns=["id","name"])

    if recipes.empty:
        st.info("Aucune recette disponible.")
    else:
        recipe_options = {row['name']: row['id'] for _, row in recipes.iterrows()}
        chosen = st.selectbox("Choisir une recette", options=list(recipe_options.keys()))
        if st.button("Ajouter ingrédients manquants depuis la recette"):
            rid = recipe_options[chosen]
            # fetch recipe ingredients
            ing_rows = cursor.execute("""
                                      SELECT i.id as ingredient_id, i.name as name, ri.quantity as qty, i.unit as unit
                                      FROM recipe_ingredients ri
                                               JOIN ingredients i ON ri.ingredient_id = i.id
                                      WHERE ri.recipe_id = ?
                                      """, (rid,)).fetchall()
            inv_map = read_inventory(cursor)
            added = 0
            for ir in ing_rows:
                iname = ir['name'] if isinstance(ir, dict) else ir[1]
                needed = float(ir['qty'] if isinstance(ir, dict) else (ir[2] or 0.0))
                norm = normalize_name(iname)
                inv = inv_map.get(norm)
                if inv and inv['quantity'] >= needed:
                    # present enough, skip
                    continue
                # If a course for same inventory exists, update qty; else insert
                if inv:
                    item_id = inv['id']
                    exist = cursor.execute("SELECT id, needed_quantity FROM courses WHERE item_id = ?", (item_id,)).fetchone()
                    if exist:
                        exist_id = exist['id'] if isinstance(exist, dict) else exist[0]
                        exist_qty = exist['needed_quantity'] if isinstance(exist, dict) else exist[1]
                        new_qty = float(exist_qty) + max(needed - inv['quantity'], 0.0)
                        cursor.execute("UPDATE courses SET needed_quantity = ? WHERE id = ?", (max(new_qty, 0.0), exist_id))
                    else:
                        qty_to_add = max(needed - (inv['quantity'] or 0.0), 0.0)
                        if qty_to_add > 0:
                            cursor.execute("INSERT INTO courses (item_id, needed_quantity) VALUES (?, ?)", (item_id, qty_to_add))
                            added += 1
                else:
                    # no inventory match; add a bare course entry (item_id NULL)
                    cursor.execute("INSERT INTO courses (item_id, needed_quantity) VALUES (?, ?)", (None, needed))
                    added += 1
            conn.commit()
            st.success(f"{added} items ajoutés à la liste (ou mis à jour).")
            st.experimental_rerun()

    st.markdown("---")

    # Generate from a batch meal: add all ingredients for a scheduled batch
    st.subheader("🍱 Générer depuis un repas batch planifié")
    try:
        df_batches = pd.read_sql("""
                                 SELECT bm.id, bm.scheduled_date, r.name as recipe_name, bm.recipe_id
                                 FROM batch_meals bm
                                          LEFT JOIN recipes r ON bm.recipe_id = r.id
                                 ORDER BY bm.scheduled_date DESC
                                 """, conn)
    except Exception:
        df_batches = pd.DataFrame(columns=["id","scheduled_date","recipe_name","recipe_id"])

    if df_batches.empty:
        st.info("Aucun batch meal planifié.")
    else:
        batch_map = {f"{row['recipe_name']} — {row['scheduled_date']}": row['id'] for _, row in df_batches.iterrows()}
        chosen_batch = st.selectbox("Choisir un batch", options=list(batch_map.keys()))
        if st.button("Ajouter ingrédients du batch"):
            bid = batch_map[chosen_batch]
            # get ingredients for batch's recipe
            ing_rows = cursor.execute("""
                                      SELECT i.id as ingredient_id, i.name as name, ri.quantity as qty
                                      FROM batch_meal_items bmi
                                               JOIN ingredients i ON bmi.ingredient_id = i.id
                                               JOIN recipe_ingredients ri ON ri.ingredient_id = i.id AND ri.recipe_id = (
                                          SELECT recipe_id FROM batch_meals WHERE id = ?
                                      )
                                      WHERE bmi.batch_meal_id = ?
                                      """, (bid, bid)).fetchall()
            inv_map = read_inventory(cursor)
            added = 0
            for ir in ing_rows:
                name = ir['name'] if isinstance(ir, dict) else ir[1]
                needed = float(ir['qty'] if isinstance(ir, dict) else (ir[2] or 0.0))
                norm = normalize_name(name)
                inv = inv_map.get(norm)
                if inv and inv['quantity'] >= needed:
                    continue
                if inv:
                    item_id = inv['id']
                    exist = cursor.execute("SELECT id, needed_quantity FROM courses WHERE item_id = ?", (item_id,)).fetchone()
                    if exist:
                        exist_id = exist['id'] if isinstance(exist, dict) else exist[0]
                        exist_qty = exist['needed_quantity'] if isinstance(exist, dict) else exist[1]
                        new_qty = float(exist_qty) + max(needed - inv['quantity'], 0.0)
                        cursor.execute("UPDATE courses SET needed_quantity = ? WHERE id = ?", (new_qty, exist_id))
                    else:
                        qty_to_add = max(needed - inv['quantity'], 0.0)
                        if qty_to_add > 0:
                            cursor.execute("INSERT INTO courses (item_id, needed_quantity) VALUES (?, ?)", (item_id, qty_to_add))
                            added += 1
                else:
                    cursor.execute("INSERT INTO courses (item_id, needed_quantity) VALUES (?, ?)", (None, needed))
                    added += 1
            conn.commit()
            st.success(f"{added} éléments ajoutés/mis à jour depuis le batch.")
            st.experimental_rerun()

    st.markdown("---")

    # Mark as purchased: choose course items and convert to inventory (deduct)
    st.subheader("✅ Marquer comme acheté / Convertir en inventaire")
    df_courses2 = read_courses_as_df(conn)
    if not df_courses2.empty:
        sel_options = [f"{row['item_name']} — {row['needed_quantity']}" for _, row in df_courses2.iterrows()]
        chosen_buy = st.selectbox("Sélectionner item acheté", options=sel_options)
        if st.button("Marquer comme acheté (déduire du stock / créer si besoin)"):
            # parse chosen_buy
            idx = sel_options.index(chosen_buy)
            row = df_courses2.iloc[idx]
            course_id = int(row['id'])
            item_name = row['item_name']
            needed = float(row['needed_quantity'] or 0.0)

            inv = read_inventory(cursor).get(normalize_name(item_name))
            try:
                if inv:
                    # update inventory quantity (add purchased amount)
                    new_qty = inv['quantity'] + needed
                    cursor.execute("UPDATE inventory_items SET quantity = ? WHERE id = ?", (new_qty, inv['id']))
                    # remove course entry
                    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
                    conn.commit()
                    st.success(f"Acheté : {item_name}. Inventaire mis à jour (+{needed}).")
                else:
                    # create inventory item and remove course
                    cursor.execute("INSERT INTO inventory_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)",
                                   (item_name, None, needed, None))
                    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
                    conn.commit()
                    st.success(f"Acheté et ajouté à l'inventaire : {item_name} ({needed}).")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erreur lors du marquage comme acheté : {e}")

    st.markdown("---")
    st.info("Astuce : utilisez 'Générer depuis une recette' pour ajouter automatiquement ce qui manque, puis marquez acheté une fois rentré(e) du supermarché.")

    conn.close()